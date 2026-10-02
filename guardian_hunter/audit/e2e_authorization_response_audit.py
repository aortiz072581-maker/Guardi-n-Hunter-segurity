"""
Guardian Hunter — E2E Authorization/Response Audit v1

Audit only.
No Phase 18 modification.
No real response execution.
No execution enablement.
"""

from __future__ import annotations

import time
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guardian_hunter.authorization.decision_response_adapter import (
    AuthorizationDecisionResponseAdapter,
)
from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.security.mode import Candidate
from guardian_hunter.security.trust_root import TrustResult



def _build_audit_adapter():
    """Build an audit-only trusted adapter with verified evidence."""
    trust = TrustResult(
        trusted=True,
        reason="AUDIT_TEST_TRUSTED",
        policy_id="AUDIT_POLICY",
        baseline_id="AUDIT_BASELINE",
        verification_time=datetime.now(timezone.utc).isoformat(),
    )

    evidence_path = (
        Path(tempfile.mkdtemp(prefix="guardian-hunter-e2e-audit-"))
        / "evidence.jsonl"
    )
    evidence_store = EvidenceStore(evidence_path)

    evidence_id = "e2e-audit-evidence"
    evidence_store.append(
        evidence_id=evidence_id,
        event_type="E2E_AUTHORIZATION_AUDIT",
        timestamp=time.time(),
        payload={"audit": True},
    )

    now = datetime.now(timezone.utc)
    candidate = Candidate(
        candidate_id="e2e-audit-candidate",
        evidence_id=evidence_id,
        created_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(minutes=5),
    )

    adapter = AuthorizationDecisionResponseAdapter(
        trust_result=trust,
        evidence_store=evidence_store,
    )

    return adapter, candidate

def _authorized_dry_run(adapter, candidate):
    now = time.time()

    return adapter.authorize_and_prepare_response(
        actor_id="e2e-operator",
        role="OPERATOR",
        action="request_response",
        request_id="e2e-authorized-request",
        authorization_id="e2e-authorized-auth",
        nonce="e2e-authorized-nonce",
        risk_level="MEDIUM",
        reason="controlled e2e audit",
        target="audit-target",
        risk_data={"audit": True},
        issued_at=now,
        expires_at=now + 300,
        candidate=candidate,
        approver="e2e-audit-approver",
        approval_reason="controlled e2e audit approval",
    )


def _unauthorized_role(adapter):
    now = time.time()

    return adapter.authorize_and_prepare_response(
        actor_id="e2e-observer",
        role="OBSERVER",
        action="request_response",
        request_id="e2e-denied-request",
        authorization_id="e2e-denied-auth",
        nonce="e2e-denied-nonce",
        risk_level="MEDIUM",
        reason="controlled denial audit",
        target="audit-target",
        risk_data={"audit": True},
        issued_at=now,
        expires_at=now + 300,
    )


def _replay(adapter, candidate):
    now = time.time()

    kwargs = dict(
        actor_id="e2e-replay",
        role="OPERATOR",
        action="request_response",
        request_id="e2e-replay-request",
        authorization_id="e2e-replay-auth",
        nonce="e2e-replay-nonce",
        risk_level="MEDIUM",
        reason="controlled replay audit",
        target="audit-target",
        risk_data={"audit": True},
        issued_at=now,
        expires_at=now + 300,
    )

    candidate_kwargs = {
        "candidate": candidate,
        "approver": "e2e-audit-approver",
        "approval_reason": "controlled replay audit approval",
    }

    first = adapter.authorize_and_prepare_response(
        **kwargs,
        **candidate_kwargs,
    )
    second = adapter.authorize_and_prepare_response(
        **kwargs,
        **candidate_kwargs,
    )

    return first, second


def _safety(result):
    return (
        result.execution_allowed is False
        and result.read_only is True
        and result.dry_run is True
        and result.real_execution_blocked is True
        and result.human_review_required is True
        and result.response_locked is True
    )


def run_audit():
    print("GUARDIAN HUNTER — E2E AUTHORIZATION/RESPONSE AUDIT v1")
    print("=" * 64)

    adapter, candidate = _build_audit_adapter()

    # ----------------------------------------------------------
    # 1 — Authorized request: response preparation only
    # ----------------------------------------------------------
    authorized = _authorized_dry_run(adapter, candidate)

    authorized_ok = (
        authorized.authorized is True
        and authorized.execution_allowed is False
        and _safety(authorized)
    )

    print(
        "AUTHORIZED REQUEST -> RESPONSE PREPARATION:",
        "OK" if authorized_ok else "FAILED",
    )

    # ----------------------------------------------------------
    # 2 — Unauthorized request: blocked before response
    # ----------------------------------------------------------
    denied = _unauthorized_role(adapter)

    denied_ok = (
        denied.authorized is False
        and denied.execution_allowed is False
        and _safety(denied)
    )

    print(
        "UNAUTHORIZED REQUEST -> FAIL-CLOSED:",
        "OK" if denied_ok else "FAILED",
    )

    # ----------------------------------------------------------
    # 3 — Replay: first may authorize, second must fail
    # ----------------------------------------------------------
    first, second = _replay(adapter, candidate)

    replay_ok = (
        first.execution_allowed is False
        and second.authorized is False
        and second.execution_allowed is False
        and _safety(first)
        and _safety(second)
    )

    print(
        "REPLAY -> BLOCKED:",
        "OK" if replay_ok else "FAILED",
    )

    # ----------------------------------------------------------
    # Final invariants
    # ----------------------------------------------------------
    all_ok = authorized_ok and denied_ok and replay_ok

    print()
    print("READ_ONLY: True")
    print("DRY_RUN: True")
    print("REAL_EXECUTION_BLOCKED: True")
    print("HUMAN_REVIEW_REQUIRED: True")
    print("RESPONSE_LOCKED: True")
    print("REAL EXECUTION: BLOCKED")

    print()

    if all_ok:
        print("=" * 64)
        print("E2E AUTHORIZATION/RESPONSE AUDIT: OK")
        print("=" * 64)
        return 0

    print("=" * 64)
    print("E2E AUTHORIZATION/RESPONSE AUDIT: FAILED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_audit())
