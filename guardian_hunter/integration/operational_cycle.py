"""Guardian Hunter supervised operational cycle.

Connects the existing defensive components without granting autonomous
authority over trust boundaries, commits, merges, or trusted baselines.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from guardian_hunter.auditor.engine import audit_extended_security
from guardian_hunter.integration.health_recovery import run_health_recovery
from guardian_hunter.integration.problem_advisor import advise_health_result
from guardian_hunter.harness.provider_runtime import discover_provider_runtimes
from guardian_hunter.integration.codex_supervised import (
    prepare_codex_candidate,
)
from guardian_hunter.integration.automatic_repair import (
    AutomaticRepairCandidate,
    execute_candidate_batch,
)
from guardian_hunter.repair.proposal import RepairProposal


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROTECTED_PREFIXES = (
    ".git/",
    ".guardian/",
    "guardian_hunter/gate/",
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
    "guardian_hunter/auditor/",
    "guardian_hunter/repair/",
    "guardian_hunter/runner/",
)

AUTOMATIC_COMMIT = False
AUTOMATIC_BASELINE_UPDATE = False
AUTOMATIC_MERGE = False
HUMAN_APPROVAL_FOR_PROTECTED = True


def _tool(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {
        "name": name,
        "available": path is not None,
        "path": path,
    }


def discover_tools() -> dict[str, dict[str, Any]]:
    names = (
        "python",
        "python3",
        "pytest",
        "git",
        "nuclei",
        "semgrep",
        "bandit",
        "ruff",
        "mypy",
        "shellcheck",
        "trivy",
        "gitleaks",
        "claude",
        "aider",
        "codex",
    )
    return {name: _tool(name) for name in names}


def _is_protected(path: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


def classify_repair_authority(
    affected_files: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    protected = tuple(path for path in affected_files if _is_protected(path))

    return {
        "affected_files": tuple(affected_files),
        "protected_files": protected,
        "low_risk_candidate": not protected,
        "automatic_apply_allowed": False,
        "human_approval_required": True,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "merge_allowed": False,
    }


def _finding_to_dict(finding: Any) -> dict[str, Any]:
    if hasattr(finding, "__dataclass_fields__"):
        return {
            name: getattr(finding, name)
            for name in finding.__dataclass_fields__
        }

    if isinstance(finding, dict):
        return dict(finding)

    return {
        "finding_id": getattr(finding, "finding_id", "UNKNOWN"),
        "severity": str(getattr(finding, "severity", "UNKNOWN")),
        "summary": getattr(
            finding,
            "summary",
            getattr(finding, "title", repr(finding)),
        ),
    }


def run_internal_review() -> dict[str, Any]:
    findings = tuple(audit_extended_security())

    return {
        "engine": "guardian_hunter.auditor",
        "executed": True,
        "finding_count": len(findings),
        "findings": [_finding_to_dict(finding) for finding in findings],
    }


def external_ai_status(
    tools: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Report verified external AI readiness without granting execution."""

    del tools  # Native Android launchers are not trusted for provider readiness.

    providers = discover_provider_runtimes()

    available = [
        name
        for name, state in providers.items()
        if state["operational"]
    ]

    return {
        "requested": True,
        "available_providers": available,
        "providers": providers,
        "executed": False,
        "reason": (
            "NO_EXTERNAL_AI_PROVIDER_OPERATIONAL"
            if not available
            else "PROVIDER_OPERATIONAL_BUT_SUPERVISED_LAUNCH_REQUIRED"
        ),
        "containment_required": True,
        "git_access_allowed": False,
        "baseline_modification_allowed": False,
        "automatic_merge_allowed": False,
    }


def nuclei_status(
    *,
    target: str | None = None,
    authorized: bool = False,
    tools: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tools = tools or discover_tools()
    installed = tools["nuclei"]["available"]

    if not installed:
        reason = "NUCLEI_UNAVAILABLE"
    elif not target:
        reason = "NO_AUTHORIZED_TARGET"
    elif not authorized:
        reason = "TARGET_NOT_AUTHORIZED"
    else:
        reason = "AUTHORIZED_TARGET_READY"

    return {
        "available": installed,
        "target": target,
        "authorized": bool(target and authorized),
        "executed": False,
        "reason": reason,
    }


def build_repair_proposals(
    findings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []

    for finding in findings:
        affected = finding.get("affected_files", ())
        if isinstance(affected, str):
            affected = (affected,)
        else:
            affected = tuple(affected or ())

        authority = classify_repair_authority(affected)

        proposals.append(
            {
                "finding_id": finding.get("finding_id", "UNKNOWN"),
                "summary": finding.get(
                    "summary",
                    finding.get("title", "Security finding"),
                ),
                "affected_files": affected,
                "authority": authority,
                "proposal_class": RepairProposal.__name__,
                "prepared": True,
                "applied": False,
                "human_approval_required": True,
            }
        )

    return proposals


def prepare_supervised_codex_candidates(
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Prepare exact ordinary candidates without repository mutation."""

    candidates: list[AutomaticRepairCandidate] = []
    results: list[dict[str, Any]] = []

    for finding in findings:
        affected = finding.get(
            "affected_files",
            (),
        )

        if isinstance(affected, str):
            affected_files = (affected,)
        else:
            affected_files = tuple(
                affected or ()
            )

        authority = classify_repair_authority(
            list(affected_files)
        )

        # Any protected member human-gates the entire finding.
        if authority["protected_files"]:
            for relative_path in affected_files:
                results.append(
                    {
                        "finding_id": finding.get(
                            "finding_id",
                            "UNKNOWN",
                        ),
                        "relative_path": relative_path,
                        "prepared": False,
                        "provider_invoked": False,
                        "reason": (
                            "PROTECTED_REPAIR_REQUIRES_"
                            "HUMAN_APPROVAL"
                        ),
                    }
                )

            continue

        for relative_path in affected_files:
            result = prepare_codex_candidate(
                finding=finding,
                relative_path=relative_path,
                root=PROJECT_ROOT,
            )

            results.append(
                {
                    "finding_id": finding.get(
                        "finding_id",
                        "UNKNOWN",
                    ),
                    "relative_path": relative_path,
                    "prepared": result.prepared,
                    "reason": result.reason,
                    "metadata": result.metadata,
                }
            )

            if (
                result.prepared
                and result.candidate is not None
            ):
                candidates.append(
                    result.candidate
                )

    return {
        "candidates": tuple(candidates),
        "results": results,
    }


def run_operational_cycle(
    *,
    target: str | None = None,
    target_authorized: bool = False,
    repair_candidates: tuple[AutomaticRepairCandidate, ...] = (),
    baseline: str | None = None,
    repair_reverifier=None,
    supervised_codex: bool = False,
    automatic_repair_enabled: bool = False,
) -> dict[str, Any]:
    """Run one fail-closed operational review cycle."""

    tools = discover_tools()

    health = run_health_recovery()
    advice = advise_health_result(health)

    review = run_internal_review()
    proposals = build_repair_proposals(review["findings"])

    codex_preparation: dict[str, Any] = {
        "enabled": supervised_codex,
        "candidate_count": 0,
        "results": [],
    }

    effective_candidates = tuple(
        repair_candidates
    )

    if (
        supervised_codex
        and review["findings"]
    ):
        prepared = (
            prepare_supervised_codex_candidates(
                review["findings"]
            )
        )

        generated_candidates = prepared[
            "candidates"
        ]

        effective_candidates = (
            effective_candidates
            + generated_candidates
        )

        codex_preparation = {
            "enabled": True,
            "candidate_count": len(
                generated_candidates
            ),
            "results": prepared["results"],
        }

    ai = external_ai_status(tools)
    ai["supervised_codex"] = codex_preparation
    nuclei = nuclei_status(
        target=target,
        authorized=target_authorized,
        tools=tools,
    )

    automatic_repairs: dict[str, Any] = {
        "candidate_count": len(effective_candidates),
        "processed_count": 0,
        "results": [],
        "filesystem_changed": False,
        "filesystem_state_uncertain": False,
        "automatic_commit": False,
        "automatic_merge": False,
        "automatic_baseline_update": False,
    }

    if effective_candidates:
        if not automatic_repair_enabled:
            automatic_repairs["results"] = [
                {
                    "status": "PREPARED_ONLY",
                    "reason": (
                        "AUTOMATIC_REPAIR_NOT_ENABLED"
                    ),
                    "applied": False,
                    "automatic": False,
                    "human_review_required": True,
                }
            ]
        elif baseline is None:
            automatic_repairs["results"] = [
                {
                    "status": "REFUSED",
                    "reason": "TRUSTED_BASELINE_REQUIRED",
                    "applied": False,
                    "automatic": False,
                    "human_review_required": True,
                }
            ]
        else:
            automatic_repairs["results"] = [{"status": "REFUSED", "reason": "M5_AUTO_REPAIR_EXTERNAL_AUTHORIZATION_REQUIRED", "applied": False, "automatic": False, "human_review_required": True}]

    blocked = (
        health.get("status") != "HEALTHY"
        or review["finding_count"] > 0
        or automatic_repairs["filesystem_state_uncertain"]
    )

    return {
        "status": "REVIEW_REQUIRED" if blocked else "HEALTHY",
        "trust_policy": {
            "automatic_commit": False,
            "automatic_baseline_update": False,
            "automatic_merge": False,
            "human_approval_for_protected": True,
        },
        "tools": tools,
        "health": health,
        "diagnosis": advice,
        "audit": review,
        "ai": ai,
        "repair": {
            "proposal_count": len(proposals),
            "proposals": proposals,
            "automatic_apply": bool(effective_candidates) and automatic_repair_enabled,
            "automatic_scope": "EXACT_NON_PROTECTED_ACTIONS_ONLY",
            "provider_authority": "PROPOSAL_ONLY",
            "automatic_repair_enabled": automatic_repair_enabled,
            "automatic_results": automatic_repairs,
            "human_approval_required_for_protected": True,
        },
        "nuclei": nuclei,
        "reverification": {
            "required_after_change": True,
            "pytest_required": True,
            "auditor_required": True,
            "diff_check_required": True,
        },
        "evidence": {
            "final_evidence_required": True,
        },
        "execution_allowed": False,
    }


__all__ = [
    "AUTOMATIC_COMMIT",
    "AUTOMATIC_BASELINE_UPDATE",
    "AUTOMATIC_MERGE",
    "HUMAN_APPROVAL_FOR_PROTECTED",
    "discover_tools",
    "classify_repair_authority",
    "run_internal_review",
    "external_ai_status",
    "nuclei_status",
    "build_repair_proposals",
    "run_operational_cycle",
]


# ---------------------------------------------------------------------------
# Supervised transactional repair
# ---------------------------------------------------------------------------

from guardian_hunter.repair.approval import (
    ApprovalLedger,
    HumanApproval,
)
from guardian_hunter.repair.executor import (
    RepairAction,
    apply_repair,
    capture_backup,
    rollback_repair,
)


def _transaction_reverification() -> dict[str, Any]:
    """Run the existing Guardian Hunter verification after a real repair."""

    import subprocess
    import sys

    pytest_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )

    pytest_output = (
        pytest_result.stdout.strip()
        or pytest_result.stderr.strip()
    )

    try:
        audit_findings = tuple(audit_extended_security())
        auditor_ok = len(audit_findings) == 0
        auditor_error = None
    except Exception as exc:
        audit_findings = ()
        auditor_ok = False
        auditor_error = f"{type(exc).__name__}: {exc}"

    diff_result = subprocess.run(
        ["git", "diff", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    passed = (
        pytest_result.returncode == 0
        and auditor_ok
        and diff_result.returncode == 0
    )

    return {
        "passed": passed,
        "pytest": {
            "passed": pytest_result.returncode == 0,
            "returncode": pytest_result.returncode,
            "summary": pytest_output[-2000:],
        },
        "auditor": {
            "passed": auditor_ok,
            "finding_count": len(audit_findings),
            "error": auditor_error,
        },
        "diff_check": {
            "passed": diff_result.returncode == 0,
            "returncode": diff_result.returncode,
            "output": (
                diff_result.stdout.strip()
                or diff_result.stderr.strip()
            ),
        },
    }



def run_supervised_automatic_repair(
    *,
    finding: dict[str, Any],
    relative_path: str,
    baseline: str,
    root: Path = PROJECT_ROOT,
    reverifier=None,
) -> dict[str, Any]:
    """Supervised automatic repair for one exact ordinary path.

    Codex has proposal authority only.

    Guardian validates the exact candidate and SHA-256
    precondition before the transactional repair layer
    receives it.

    Protected boundaries never receive automatic mutation
    authority.

    Commit, merge and trusted-baseline mutation remain
    outside this function's authority.
    """

    return {"status": "REFUSED", "reason": "M5_AUTO_REPAIR_EXTERNAL_AUTHORIZATION_REQUIRED", "applied": False, "automatic": False, "human_review_required": True, "commit_allowed": False, "merge_allowed": False, "baseline_update_allowed": False}

    root = root.resolve()

    authority = classify_repair_authority(
        [relative_path]
    )

    if authority["protected_files"]:
        return {
            "status": "APPROVAL_REQUIRED",
            "reason": (
                "PROTECTED_REPAIR_REQUIRES_HUMAN_APPROVAL"
            ),
            "authority": authority,
            "provider_invoked": False,
            "candidate_prepared": False,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    if not authority.get(
        "low_risk_candidate",
        False,
    ):
        return {
            "status": "REFUSED",
            "reason": "AUTOMATIC_AUTHORITY_NOT_GRANTED",
            "authority": authority,
            "provider_invoked": False,
            "candidate_prepared": False,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    codex_result = prepare_codex_candidate(
        finding=finding,
        relative_path=relative_path,
        root=root,
    )

    if not codex_result.prepared:
        return {
            "status": "PROPOSAL_NOT_PREPARED",
            "reason": codex_result.reason,
            "authority": authority,
            "provider": dict(
                codex_result.metadata
            ),
            "provider_invoked": bool(
                codex_result.metadata.get(
                    "provider_invoked",
                    False,
                )
            ),
            "candidate_prepared": False,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    candidate = codex_result.candidate

    if candidate is None:
        return {
            "status": "REFUSED",
            "reason": "CODEX_CANDIDATE_MISSING",
            "authority": authority,
            "provider": dict(
                codex_result.metadata
            ),
            "provider_invoked": True,
            "candidate_prepared": False,
            "applied": False,
            "rolled_back": False,
            "automatic": False,
            "human_review_required": True,
            "commit_allowed": False,
            "merge_allowed": False,
            "baseline_update_allowed": False,
        }

    # Critical boundary:
    # use the exact validated candidate returned by Codex
    # integration. Never reconstruct RepairAction here.
    result = execute_automatic_candidate(
        candidate=candidate,
        baseline=baseline,
        transaction_runner=run_transactional_repair,
        authority_classifier=classify_repair_authority,
        root=root,
        reverifier=reverifier,
    )

    result = dict(result)

    result["provider"] = dict(
        codex_result.metadata
    )
    result["provider_invoked"] = True
    result["candidate_prepared"] = True

    # Authority narrowing is unconditional.
    result["commit_allowed"] = False
    result["merge_allowed"] = False
    result["baseline_update_allowed"] = False
    result["human_review_required"] = True

    return result


def run_transactional_repair(
    *,
    proposal: RepairProposal,
    action: RepairAction,
    baseline: str,
    approval: HumanApproval | None = None,
    approval_ledger: ApprovalLedger | None = None,
    root: Path = PROJECT_ROOT,
    reverifier=None,
) -> dict[str, Any]:
    """Execute one supervised repair transaction.

    Flow:
        proposal
        -> authority classification
        -> approval when protected
        -> exact backup
        -> real repair
        -> reverification
        -> retain for human review on PASS
        -> automatic rollback on FAIL

    This function has no authority to commit, merge, or update the
    trusted baseline.
    """

    from guardian_hunter.supply_chain.m5_transaction_gate import enforce_transaction
    enforce_transaction(proposal=proposal, action=action, baseline=baseline, approval=approval, root=root)

    root = root.resolve()

    authority = classify_repair_authority(
        list(proposal.affected_files)
    )

    relative_path = action.relative_path

    if relative_path not in proposal.affected_files:
        return {
            "status": "REFUSED",
            "reason": "ACTION_NOT_IN_PROPOSAL",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    protected = relative_path in authority["protected_files"]

    if protected and approval is None:
        return {
            "status": "APPROVAL_REQUIRED",
            "reason": "PROTECTED_REPAIR_REQUIRES_HUMAN_APPROVAL",
            "authority": authority,
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    backup = capture_backup(
        root=root,
        relative_path=relative_path,
    )

    # Policy context for approval verification (same as verifier)
    policy_ctx = {
        "execution_allowed": False,
        "merge_allowed": False,
        "automatic_apply": False,
        "human_approval_required": True,
        "baseline": baseline,
    }
    apply_result = apply_repair(
        root=root,
        proposal=proposal,
        action=action,
        baseline=baseline,
        approval=approval,
        approval_ledger=approval_ledger,
        policy=policy_ctx,
    )

    if not apply_result.applied:
        return {
            "status": "REFUSED",
            "reason": apply_result.reason,
            "authority": authority,
            "apply": {
                "applied": False,
                "reason": apply_result.reason,
                "before_sha256": apply_result.before_sha256,
                "after_sha256": apply_result.after_sha256,
                "approval_verified": apply_result.approval_verified,
            },
            "applied": False,
            "rolled_back": False,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    verifier = reverifier or _transaction_reverification

    try:
        verification = verifier()
    except Exception as exc:
        verification = {
            "passed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    if not bool(verification.get("passed")):
        rollback = rollback_repair(
            root=root,
            backup=backup,
            expected_current_sha256=apply_result.after_sha256,
        )

        return {
            "status": (
                "ROLLED_BACK"
                if rollback.applied
                else "ROLLBACK_FAILED"
            ),
            "reason": (
                "REVERIFICATION_FAILED"
                if rollback.applied
                else "REVERIFICATION_FAILED_AND_ROLLBACK_FAILED"
            ),
            "authority": authority,
            "apply": {
                "applied": True,
                "reason": apply_result.reason,
                "before_sha256": apply_result.before_sha256,
                "after_sha256": apply_result.after_sha256,
                "approval_verified": apply_result.approval_verified,
            },
            "verification": verification,
            "rollback": {
                "applied": rollback.applied,
                "reason": rollback.reason,
                "after_sha256": rollback.after_sha256,
            },
            "applied": False,
            "rolled_back": rollback.applied,
            "human_review_required": True,
            "commit_allowed": False,
            "baseline_update_allowed": False,
            "merge_allowed": False,
        }

    return {
        "status": "REPAIR_PENDING_HUMAN_REVIEW",
        "reason": "REPAIR_APPLIED_AND_REVERIFIED",
        "authority": authority,
        "apply": {
            "applied": True,
            "reason": apply_result.reason,
            "before_sha256": apply_result.before_sha256,
            "after_sha256": apply_result.after_sha256,
            "approval_verified": apply_result.approval_verified,
        },
        "verification": verification,
        "rollback": {
            "applied": False,
            "reason": "NOT_REQUIRED",
        },
        "applied": True,
        "rolled_back": False,
        "human_review_required": True,
        "commit_allowed": False,
        "baseline_update_allowed": False,
        "merge_allowed": False,
    }


__all__.extend(
    [
        "run_transactional_repair",
        "run_supervised_automatic_repair",
    ]
)
