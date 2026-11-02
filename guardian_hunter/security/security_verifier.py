"""
Guardian Hunter permanent adversarial security verifier.

This verifier grants no execution, commit, merge, or trust-root authority.

Every PASS/DENIED result is produced by an actual security check.
Unknown or unimplemented guarantees must never be reported as PASS.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable
import hashlib
import json

from guardian_hunter.security.authorization_binding import (
    create_binding,
    verify_binding,
)
from guardian_hunter.evidence.incident import (
    create_incident_record,
    verify_incident_record,
)
from guardian_hunter.evidence.persistence import (
    EvidenceStore,
    fail_closed as evidence_fail_closed,
)
from guardian_hunter.harness.broker import (
    CREDENTIAL_NAMES,
    prepare,
    sanitized_environment,
)
from guardian_hunter.harness.launcher import LaunchRequest
from guardian_hunter.execution.supervised_gate import (
    GLOBAL_EXECUTION_ALLOWED,
    COMMIT_ALLOWED,
    MERGE_ALLOWED,
    BASELINE_UPDATE_ALLOWED,
    execute_supervised_transaction,
)
from guardian_hunter.repair.proposal import RepairProposal
from guardian_hunter.repair.executor import RepairAction
from guardian_hunter.repair.approval import (
    HumanApproval,
    ApprovalLedger,
)
from guardian_hunter.gate.core import evaluate_candidate
from guardian_hunter.policy.opa_guard import evaluate_opa
from guardian_hunter.provenance.in_toto_verifier import (
    run_provenance_verification,
)


@dataclass(frozen=True)
class Verification:
    name: str
    state: str
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.state in {"PASS", "DENIED", "BLOCKED"}


POLICY = {
    "mode": "DRY_RUN",
    "execution_allowed": False,
    "human_review_required": True,
}


def _expect_denied(
    name: str,
    expected: str,
    action: Callable[[], object],
) -> Verification:
    try:
        action()
    except Exception as exc:
        reason = str(exc)

        if expected in reason:
            return Verification(name, "DENIED", reason)

        return Verification(
            name,
            "FAIL",
            f"unexpected refusal: {type(exc).__name__}: {reason}",
        )

    return Verification(
        name,
        "FAIL",
        "attack unexpectedly accepted",
    )


def verify_trust_root(root: Path) -> Verification:
    baseline_path = root / ".guardian" / "trusted-baseline"

    if not baseline_path.is_file():
        return Verification(
            "Trust Root",
            "FAIL",
            "TRUSTED_BASELINE_MISSING",
        )

    baseline = baseline_path.read_text(
        encoding="utf-8"
    ).strip()

    import subprocess

    try:
        head = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception as exc:
        return Verification(
            "Trust Root",
            "FAIL",
            f"GIT_HEAD_UNAVAILABLE:{type(exc).__name__}",
        )

    if head != baseline:
        return Verification(
            "Trust Root",
            "FAIL",
            "PROTECTED_HEAD_BASELINE_MISMATCH",
        )

    return Verification(
        "Trust Root",
        "PASS",
        head,
    )


def verify_authorization_binding() -> list[Verification]:
    proposal_hash = "a" * 64
    baseline = "b" * 40

    binding = create_binding(
        proposal_hash=proposal_hash,
        policy=POLICY,
        baseline=baseline,
    )

    results: list[Verification] = []

    try:
        exact = verify_binding(
            binding,
            proposal_hash=proposal_hash,
            policy=POLICY,
            baseline=baseline,
        )

        if (
            exact is True
            and binding.execution_allowed is False
            and binding.human_review_required is True
        ):
            results.append(
                Verification(
                    "Authorization Binding",
                    "PASS",
                    "exact context verified",
                )
            )
        else:
            results.append(
                Verification(
                    "Authorization Binding",
                    "FAIL",
                    "unsafe binding state",
                )
            )
    except Exception as exc:
        results.append(
            Verification(
                "Authorization Binding",
                "FAIL",
                str(exc),
            )
        )

    results.append(
        _expect_denied(
            "Post-Approval Mutation",
            "PROPOSAL_HASH_MISMATCH",
            lambda: verify_binding(
                binding,
                proposal_hash="c" * 64,
                policy=POLICY,
                baseline=baseline,
            ),
        )
    )

    changed_policy = dict(POLICY)
    changed_policy["execution_allowed"] = True

    results.append(
        _expect_denied(
            "Policy Tampering",
            "POLICY_HASH_MISMATCH",
            lambda: verify_binding(
                binding,
                proposal_hash=proposal_hash,
                policy=changed_policy,
                baseline=baseline,
            ),
        )
    )

    results.append(
        _expect_denied(
            "Baseline Tampering",
            "BASELINE_MISMATCH",
            lambda: verify_binding(
                binding,
                proposal_hash=proposal_hash,
                policy=POLICY,
                baseline="d" * 40,
            ),
        )
    )

    authority_attack = replace(
        binding,
        execution_allowed=True,
    )

    results.append(
        _expect_denied(
            "Authorization Escalation",
            "EXECUTION_AUTHORITY_FORBIDDEN",
            authority_attack.validate,
        )
    )

    return results


def verify_incident_evidence() -> list[Verification]:
    record = create_incident_record(
        incident_id="GH-SECURITY-VERIFY",
        decision={
            "execution_allowed": False,
            "response_locked": True,
        },
        evidence=[
            {
                "type": "security-verification",
                "value": "original",
            }
        ],
    )

    results: list[Verification] = []

    if verify_incident_record(record):
        results.append(
            Verification(
                "Incident Evidence Integrity",
                "PASS",
                "SHA256 verified",
            )
        )
    else:
        results.append(
            Verification(
                "Incident Evidence Integrity",
                "FAIL",
                "valid record rejected",
            )
        )

    corrupted = dict(record)
    corrupted["decision"] = dict(record["decision"])
    corrupted["decision"]["execution_allowed"] = True

    if not verify_incident_record(corrupted):
        results.append(
            Verification(
                "Incident Evidence Corruption",
                "DENIED",
                "hash mismatch detected",
            )
        )
    else:
        results.append(
            Verification(
                "Incident Evidence Corruption",
                "FAIL",
                "corruption accepted",
            )
        )

    return results


def verify_persistent_evidence() -> list[Verification]:
    results: list[Verification] = []

    with TemporaryDirectory(
        prefix="gh-evidence-verifier-"
    ) as td:
        path = Path(td) / "evidence.jsonl"

        store = EvidenceStore(path)

        store.append(
            evidence_id="ev-verifier-1",
            event_type="SECURITY_VERIFY",
            timestamp=1000.0,
            payload={"value": "original"},
        )

        store.append(
            evidence_id="ev-verifier-2",
            event_type="SECURITY_VERIFY",
            timestamp=1001.0,
            payload={"value": "second"},
        )

        valid = store.verify()

        if (
            valid.state == "EVIDENCE_INTEGRITY_OK"
            and valid.records == 2
            and evidence_fail_closed(valid)
        ):
            results.append(
                Verification(
                    "Evidence Chain",
                    "PASS",
                    "2 records verified",
                )
            )
        else:
            results.append(
                Verification(
                    "Evidence Chain",
                    "FAIL",
                    valid.state,
                )
            )

        lines = path.read_text(
            encoding="utf-8"
        ).splitlines()

        first = json.loads(lines[0])
        first["payload"]["value"] = "tampered"

        lines[0] = json.dumps(
            first,
            sort_keys=True,
            ensure_ascii=False,
        )

        path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        corrupted = store.verify()

        if (
            corrupted.state == "EVIDENCE_TAMPER_DETECTED"
            and corrupted.invalid_hash
            and evidence_fail_closed(corrupted)
        ):
            results.append(
                Verification(
                    "Persistent Evidence Tampering",
                    "DENIED",
                    "tamper detected; fail closed",
                )
            )
        else:
            results.append(
                Verification(
                    "Persistent Evidence Tampering",
                    "FAIL",
                    corrupted.state,
                )
            )

    return results


def verify_broker() -> list[Verification]:
    results: list[Verification] = []

    env = sanitized_environment()

    leaked = sorted(
        name
        for name in CREDENTIAL_NAMES
        if name in env
    )

    if leaked:
        results.append(
            Verification(
                "Credential Isolation",
                "FAIL",
                ",".join(leaked),
            )
        )
    else:
        results.append(
            Verification(
                "Credential Isolation",
                "PASS",
                "credential names absent",
            )
        )

    try:
        result = prepare(
            LaunchRequest(
                provider="codex",
                capability="read_workspace",
                relative_path=(
                    "guardian_hunter/analysis/engine.py"
                ),
            )
        )

        safe = (
            result.dry_run is True
            and result.executed is False
            and result.credentials_present is False
            and result.git_available is False
            and result.workspace == "/workspace"
        )

        results.append(
            Verification(
                "Broker Isolation",
                "PASS" if safe else "FAIL",
                result.reason,
            )
        )
    except Exception as exc:
        results.append(
            Verification(
                "Broker Isolation",
                "FAIL",
                str(exc),
            )
        )

    attacks = (
        (
            "Broker Git Escape",
            LaunchRequest(
                provider="claude",
                capability="git",
                relative_path=".git/config",
            ),
        ),
        (
            "Broker Path Escape",
            LaunchRequest(
                provider="aider",
                capability="shell",
                relative_path="../guardian-hunter",
            ),
        ),
        (
            "Broker Gate Modification",
            LaunchRequest(
                provider="codex",
                capability="propose_edit",
                relative_path=(
                    "guardian_hunter/gate/agent_gate.py"
                ),
            ),
        ),
        (
            "Broker Trust-Root Access",
            LaunchRequest(
                provider="aider",
                capability="read_workspace",
                relative_path=".guardian/trusted-baseline",
            ),
        ),
    )

    for name, request in attacks:
        results.append(
            _expect_denied(
                name,
                "",
                lambda request=request: prepare(request),
            )
        )

    results.append(
        _expect_denied(
            "Real Execution Bypass",
            "Real provider execution not enabled",
            lambda: prepare(
                LaunchRequest(
                    provider="codex",
                    capability="read_workspace",
                    relative_path=(
                        "guardian_hunter/analysis/engine.py"
                    ),
                ),
                dry_run=False,
            ),
        )
    )

    return results



def verify_protected_transaction(
    root: Path,
) -> list[Verification]:
    """
    Exercise the real supervised transactional path against a temporary
    protected-path sandbox.

    This verifies:
      * protected repair authorization
      * real sandbox write
      * approval consumption
      * replay denial through the supervised gate
      * failed reverification detection
      * exact automatic rollback
      * absence of commit/merge/baseline/global authority
    """

    results: list[Verification] = []

    baseline_path = root / ".guardian" / "trusted-baseline"

    if not baseline_path.is_file():
        return [
            Verification(
                "Protected Repair",
                "FAIL",
                "TRUSTED_BASELINE_MISSING",
            )
        ]

    baseline = baseline_path.read_text(
        encoding="utf-8"
    ).strip()

    original = b"ORIGINAL PROTECTED VERIFIER DATA\n"
    repaired = b"REPAIRED PROTECTED VERIFIER DATA\n"

    def sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def proposal_for(
        finding_id: str,
        relative_path: str,
        required_test: str,
    ) -> RepairProposal:
        return RepairProposal(
            finding_id=finding_id,
            summary=(
                "Permanent adversarial protected "
                "transaction verification."
            ),
            affected_files=(relative_path,),
            patch=(
                f"--- a/{relative_path}\n"
                f"+++ b/{relative_path}\n"
                "@@ verifier @@\n"
                "-ORIGINAL PROTECTED VERIFIER DATA\n"
                "+REPAIRED PROTECTED VERIFIER DATA\n"
            ),
            required_tests=(required_test,),
            automatic_apply=False,
            execution_allowed=False,
            merge_allowed=False,
            human_approval_required=True,
        )

    def approval_for(
        proposal: RepairProposal,
        nonce: str,
    ) -> HumanApproval:
        # Fixed timestamps keep the verifier deterministic while
        # remaining valid at construction time. The transactional
        # approval verifier uses current time, so use a broad but
        # finite validity interval.
        import time

        now = time.time()

        return HumanApproval(
            finding_id=proposal.finding_id,
            proposal_hash=proposal.proposal_hash,
            decision="APPROVED",
            approver_id="guardian-security-verifier",
            nonce=nonce,
            issued_at=now,
            expires_at=now + 300.0,
            baseline=baseline,
            policy_hash=None,
            automatic_apply=False,
            execution_allowed=False,
            merge_allowed=False,
        )

    with TemporaryDirectory(
        prefix="gh-protected-verifier-"
    ) as td:
        sandbox = Path(td)

        ledger_path = sandbox / "approval-ledger.jsonl"
        ledger = ApprovalLedger(ledger_path)

        # ======================================================
        # A. Successful protected transaction
        # ======================================================

        path_a = (
            "guardian_hunter/security/"
            "verifier_protected_success.txt"
        )

        target_a = sandbox / path_a
        target_a.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        target_a.write_bytes(original)

        proposal_a = proposal_for(
            "GH-9401",
            path_a,
            "security-verifier-protected-success",
        )

        approval_a = approval_for(
            proposal_a,
            "security-verifier-success-nonce",
        )

        action_a = RepairAction(
            relative_path=path_a,
            expected_sha256=sha(original),
            replacement=repaired,
        )

        def reverify_a():
            data = target_a.read_bytes()

            return {
                "passed": data == repaired,
                "sha256": sha(data),
            }

        try:
            result_a = execute_supervised_transaction(
                proposal=proposal_a,
                action=action_a,
                baseline=baseline,
                approval=approval_a,
                approval_ledger=ledger,
                root=sandbox,
                reverify=reverify_a,
            )
        except Exception as exc:
            results.append(
                Verification(
                    "Protected Repair",
                    "FAIL",
                    f"{type(exc).__name__}:{exc}",
                )
            )
            return results

        protected_success = (
            result_a.get("status")
            == "REPAIR_PENDING_HUMAN_REVIEW"
            and result_a.get("applied") is True
            and result_a.get("rolled_back") is False
            and target_a.read_bytes() == repaired
            and ledger_path.exists()
            and result_a.get("commit_allowed") is False
            and result_a.get("merge_allowed") is False
            and result_a.get(
                "baseline_update_allowed"
            ) is False
            and result_a.get(
                "global_execution_allowed"
            ) is False
        )

        results.append(
            Verification(
                "Protected Repair",
                "PASS" if protected_success else "FAIL",
                result_a.get(
                    "reason",
                    "protected transaction result invalid",
                ),
            )
        )

        # ======================================================
        # B. End-to-end approval replay
        #
        # Restore the original content so the expected_sha256
        # precondition succeeds and execution reaches the ledger.
        # The same consumed approval must then be refused.
        # ======================================================

        target_a.write_bytes(original)

        try:
            replay = execute_supervised_transaction(
                proposal=proposal_a,
                action=action_a,
                baseline=baseline,
                approval=approval_a,
                approval_ledger=ledger,
                root=sandbox,
                reverify=reverify_a,
            )

            replay_denied = (
                replay.get("status") == "REFUSED"
                and replay.get("reason")
                == "APPROVAL_REPLAYED"
                and replay.get("applied") is False
                and target_a.read_bytes() == original
            )

            results.append(
                Verification(
                    "Approval Replay",
                    (
                        "DENIED"
                        if replay_denied
                        else "FAIL"
                    ),
                    replay.get(
                        "reason",
                        "replay unexpectedly accepted",
                    ),
                )
            )

        except PermissionError as exc:
            if "APPROVAL_REPLAYED" in str(exc):
                results.append(
                    Verification(
                        "Approval Replay",
                        "DENIED",
                        str(exc),
                    )
                )
            else:
                results.append(
                    Verification(
                        "Approval Replay",
                        "FAIL",
                        str(exc),
                    )
                )
        except Exception as exc:
            results.append(
                Verification(
                    "Approval Replay",
                    "FAIL",
                    f"{type(exc).__name__}:{exc}",
                )
            )

        # ======================================================
        # C. Failed reverification -> exact rollback
        # ======================================================

        path_b = (
            "guardian_hunter/security/"
            "verifier_protected_rollback.txt"
        )

        target_b = sandbox / path_b
        target_b.write_bytes(original)

        proposal_b = proposal_for(
            "GH-9402",
            path_b,
            "security-verifier-forced-failure",
        )

        approval_b = approval_for(
            proposal_b,
            "security-verifier-rollback-nonce",
        )

        action_b = RepairAction(
            relative_path=path_b,
            expected_sha256=sha(original),
            replacement=repaired,
        )

        def reverify_b():
            return {
                "passed": False,
                "error": (
                    "INTENTIONAL_ADVERSARIAL_"
                    "REVERIFICATION_FAILURE"
                ),
            }

        try:
            result_b = execute_supervised_transaction(
                proposal=proposal_b,
                action=action_b,
                baseline=baseline,
                approval=approval_b,
                approval_ledger=ledger,
                root=sandbox,
                reverify=reverify_b,
            )

            failure_detected = (
                result_b.get("status") == "ROLLED_BACK"
                and result_b.get("reason")
                == "REVERIFICATION_FAILED"
                and result_b.get("applied") is False
                and result_b.get("rolled_back") is True
            )

            exact_rollback = (
                target_b.read_bytes() == original
                and sha(target_b.read_bytes())
                == sha(original)
            )

            authority_blocked = (
                result_b.get("commit_allowed") is False
                and result_b.get("merge_allowed") is False
                and result_b.get(
                    "baseline_update_allowed"
                ) is False
                and result_b.get(
                    "global_execution_allowed"
                ) is False
            )

            results.append(
                Verification(
                    "Failed Reverification",
                    (
                        "DENIED"
                        if failure_detected
                        else "FAIL"
                    ),
                    result_b.get(
                        "reason",
                        "failure not detected",
                    ),
                )
            )

            results.append(
                Verification(
                    "Automatic Rollback",
                    (
                        "PASS"
                        if (
                            exact_rollback
                            and authority_blocked
                        )
                        else "FAIL"
                    ),
                    (
                        "original SHA256 restored"
                        if exact_rollback
                        else "original not restored"
                    ),
                )
            )

        except Exception as exc:
            results.append(
                Verification(
                    "Failed Reverification",
                    "FAIL",
                    f"{type(exc).__name__}:{exc}",
                )
            )
            results.append(
                Verification(
                    "Automatic Rollback",
                    "FAIL",
                    "transaction raised before verification",
                )
            )

    return results


def verify_agent_authority() -> list[Verification]:
    """
    Verify that candidate/agent changes cannot grant themselves
    authority over protected Guardian boundaries.

    This does not launch an external agent.
    """

    results: list[Verification] = []

    protected_attacks = (
        "guardian_hunter/repair/approval.py",
        "guardian_hunter/security/security_verifier.py",
        "guardian_hunter/gate/agent_gate.py",
        "guardian_hunter/harness/broker.py",
    )

    for path in protected_attacks:
        try:
            result = evaluate_candidate([path])

            denied = (
                result.passed is False
                and result.human_review_required is True
                and result.agent_merge_allowed is False
                and result.reason.startswith(
                    "PROTECTED_BOUNDARY_CHANGED:"
                )
            )

            if not denied:
                return [
                    Verification(
                        "Agent Protected-Boundary Bypass",
                        "FAIL",
                        f"accepted:{path}",
                    )
                ]

        except Exception as exc:
            return [
                Verification(
                    "Agent Protected-Boundary Bypass",
                    "FAIL",
                    f"{type(exc).__name__}:{exc}",
                )
            ]

    results.append(
        Verification(
            "Agent Protected-Boundary Bypass",
            "DENIED",
            (
                f"{len(protected_attacks)} "
                "protected attacks rejected"
            ),
        )
    )

    # The broker is the only intended provider launcher and must
    # reject a request to turn on real execution.
    results.append(
        _expect_denied(
            "Agent Direct Execution",
            "Real provider execution not enabled",
            lambda: prepare(
                LaunchRequest(
                    provider="codex",
                    capability="read_workspace",
                    relative_path=(
                        "guardian_hunter/analysis/engine.py"
                    ),
                ),
                dry_run=False,
            ),
        )
    )

    return results


def verify_phase_a_security() -> list[Verification]:
    """Verify independent Phase-A security controls."""

    baseline = "c" * 40

    context = {
        "human_review_required": True,
        "execution_allowed": False,
        "merge_allowed": False,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "global_execution_allowed": False,
        "proposal_hash": "a" * 64,
        "approved_proposal_hash": "a" * 64,
        "policy_hash": "b" * 64,
        "approved_policy_hash": "b" * 64,
        "baseline": baseline,
        "approved_baseline": baseline,
    }

    opa_exact = evaluate_opa(context)

    if not opa_exact.allowed:
        raise PermissionError(
            "OPA_EXACT_CONTEXT_DENIED"
        )

    mutated = dict(context)
    mutated["proposal_hash"] = "d" * 64

    opa_mutation = evaluate_opa(mutated)

    if opa_mutation.allowed:
        raise PermissionError(
            "OPA_PROPOSAL_MUTATION_ALLOWED"
        )

    escalated = dict(context)
    escalated["execution_allowed"] = True

    opa_escalation = evaluate_opa(escalated)

    if opa_escalation.allowed:
        raise PermissionError(
            "OPA_AUTHORITY_ESCALATION_ALLOWED"
        )

    invalid_baseline = dict(context)
    invalid_baseline["baseline"] = "c" * 64
    invalid_baseline["approved_baseline"] = "c" * 64

    opa_invalid_baseline = evaluate_opa(
        invalid_baseline
    )

    if opa_invalid_baseline.allowed:
        raise PermissionError(
            "OPA_INVALID_BASELINE_ALLOWED"
        )

    provenance = run_provenance_verification()

    if not provenance.signed_provenance:
        raise PermissionError(
            "IN_TOTO_PROVENANCE_FAILED"
        )

    if not provenance.signature_verified:
        raise PermissionError(
            "IN_TOTO_SIGNATURE_FAILED"
        )

    if not provenance.artifact_mutation_denied:
        raise PermissionError(
            "IN_TOTO_ARTIFACT_MUTATION_ALLOWED"
        )

    if not provenance.metadata_tampering_denied:
        raise PermissionError(
            "IN_TOTO_METADATA_TAMPERING_ALLOWED"
        )

    return [
        Verification(
            "OPA Policy Verification",
            "PASS",
            "exact authorization context allowed",
        ),
        Verification(
            "OPA Proposal Mutation",
            "DENIED",
            "mutated proposal rejected",
        ),
        Verification(
            "OPA Authority Escalation",
            "DENIED",
            "execution escalation rejected",
        ),
        Verification(
            "OPA Invalid Baseline",
            "DENIED",
            "64-hex baseline rejected",
        ),
        Verification(
            "in-toto Provenance",
            "PASS",
            "signed Link metadata verified",
        ),
        Verification(
            "in-toto Signature",
            "PASS",
            "Ed25519 signature verified",
        ),
        Verification(
            "Artifact Mutation",
            "DENIED",
            "recorded product hash mismatch detected",
        ),
        Verification(
            "Metadata Tampering",
            "DENIED",
            "signature verification rejected tampering",
        ),
    ]


def verify_authority_boundaries() -> list[Verification]:
    values = (
        ("Commit Authority", COMMIT_ALLOWED),
        ("Merge Authority", MERGE_ALLOWED),
        (
            "Baseline Authority",
            BASELINE_UPDATE_ALLOWED,
        ),
        (
            "Global Execution",
            GLOBAL_EXECUTION_ALLOWED,
        ),
    )

    return [
        Verification(
            name,
            "BLOCKED" if value is False else "FAIL",
            "False" if value is False else "unexpected authority",
        )
        for name, value in values
    ]


def run_security_verification(
    root: Path | None = None,
) -> tuple[Verification, ...]:
    root = (
        Path.cwd()
        if root is None
        else Path(root)
    ).resolve()

    results: list[Verification] = []

    results.append(verify_trust_root(root))
    results.extend(verify_authorization_binding())
    results.extend(verify_incident_evidence())
    results.extend(verify_persistent_evidence())
    results.extend(verify_broker())
    results.extend(verify_protected_transaction(root))
    results.extend(verify_agent_authority())
    results.extend(verify_phase_a_security())
    results.extend(verify_authority_boundaries())

    from guardian_hunter.security.sensor_verification import (
        verify_sensor_evidence,
    )

    try:
        sensor_ok = verify_sensor_evidence()
    except Exception:
        sensor_ok = False

    results.append(
        Verification(
            "Sensor Evidence Integration",
            "PASS" if sensor_ok else "FAIL",
            "offline integrity and tamper checks",
        )
    )


    from guardian_hunter.security.codeql_verification import (
        verify_codeql_evidence,
    )
    try:
        codeql_ok = verify_codeql_evidence()
    except Exception:
        codeql_ok = False
    results.append(
        Verification(
            "CodeQL SARIF Evidence",
            "PASS" if codeql_ok else "FAIL",
            "offline SARIF and evidence integrity",
        )
    )

    return tuple(results)


def final_verdict(
    results: tuple[Verification, ...],
) -> bool:
    return bool(results) and all(
        result.passed
        for result in results
    )


def main() -> int:
    results = run_security_verification()

    print("GUARDIAN HUNTER SECURITY VERIFIER")
    print("=" * 56)

    for result in results:
        print(
            f"{result.name:.<34} "
            f"{result.state}"
        )

        if result.detail:
            print(f"  {result.detail}")

    print("=" * 56)

    verdict = final_verdict(results)

    print(
        f"FINAL VERDICT .................... "
        f"{'PASS' if verdict else 'FAIL'}"
    )

    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
