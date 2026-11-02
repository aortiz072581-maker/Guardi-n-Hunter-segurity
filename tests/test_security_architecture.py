from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.security.mode import (
    AuthorizationError,
    Candidate,
    Mode,
    TransitionError,
    authorize_candidate,
    transition,
)
from guardian_hunter.security.trust_root import TrustResult


def make_trust(trusted: bool) -> TrustResult:
    return TrustResult(
        trusted=trusted,
        reason=(
            "TEST_TRUSTED"
            if trusted
            else "TEST_UNTRUSTED"
        ),
        policy_id="POLICY-TEST" if trusted else None,
        baseline_id="BASELINE-TEST" if trusted else None,
        verification_time=datetime.now(
            timezone.utc
        ).isoformat(),
    )


def make_candidate(now: datetime) -> Candidate:
    return Candidate(
        candidate_id="CAND-001",
        evidence_id="EV-001",
        created_at=now,
        expires_at=now + timedelta(minutes=10),
    )


def test_req003_direct_authorized_transition_blocked():
    with pytest.raises(TransitionError):
        transition(
            Mode.OBSERVE,
            Mode.AUTHORIZED,
        )

    with pytest.raises(TransitionError):
        transition(
            Mode.CANDIDATE,
            Mode.AUTHORIZED,
        )


def test_req001_untrusted_cannot_authorize(tmp_path: Path):
    now = datetime.now(timezone.utc)

    store = EvidenceStore(
        tmp_path / "evidence.jsonl"
    )

    store.append(
        evidence_id="EV-001",
        event_type="TEST",
        timestamp=now.timestamp(),
        payload={"status": "valid"},
    )

    with pytest.raises(AuthorizationError):
        authorize_candidate(
            current=Mode.CANDIDATE,
            candidate=make_candidate(now),
            trust=make_trust(False),
            evidence_store=store,
            approver="human-01",
            reason="manual review",
            now=now,
        )


def test_req004_missing_evidence_blocks_authorization(
    tmp_path: Path,
):
    now = datetime.now(timezone.utc)

    store = EvidenceStore(
        tmp_path / "evidence.jsonl"
    )

    with pytest.raises(AuthorizationError):
        authorize_candidate(
            current=Mode.CANDIDATE,
            candidate=make_candidate(now),
            trust=make_trust(True),
            evidence_store=store,
            approver="human-01",
            reason="manual review",
            now=now,
        )


def test_req004_tampered_evidence_blocks_authorization(
    tmp_path: Path,
):
    now = datetime.now(timezone.utc)

    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path)

    store.append(
        evidence_id="EV-001",
        event_type="TEST",
        timestamp=now.timestamp(),
        payload={"status": "valid"},
    )

    text = path.read_text()

    path.write_text(
        text.replace(
            '"valid"',
            '"tampered"',
        )
    )

    with pytest.raises(AuthorizationError):
        authorize_candidate(
            current=Mode.CANDIDATE,
            candidate=make_candidate(now),
            trust=make_trust(True),
            evidence_store=store,
            approver="human-01",
            reason="manual review",
            now=now,
        )


def test_req005_authorization_preserves_provenance(
    tmp_path: Path,
):
    now = datetime.now(timezone.utc)

    store = EvidenceStore(
        tmp_path / "evidence.jsonl"
    )

    store.append(
        evidence_id="EV-001",
        event_type="TEST",
        timestamp=now.timestamp(),
        payload={"status": "valid"},
    )

    mode, provenance = authorize_candidate(
        current=Mode.CANDIDATE,
        candidate=make_candidate(now),
        trust=make_trust(True),
        evidence_store=store,
        approver="human-01",
        reason="evidence reviewed",
        now=now,
    )

    assert mode is Mode.AUTHORIZED
    assert provenance.candidate_id == "CAND-001"
    assert provenance.evidence_id == "EV-001"
    assert provenance.approver == "human-01"
    assert provenance.reason == "evidence reviewed"
    assert provenance.authorized_at == now


def test_req003_adapter_requires_candidate_for_response(
    tmp_path: Path,
):
    from time import time

    from guardian_hunter.authorization.contract import Role
    from guardian_hunter.authorization.decision_response_adapter import (
        AuthorizationDecisionResponseAdapter,
    )

    store = EvidenceStore(
        tmp_path / "adapter-evidence.jsonl"
    )

    adapter = AuthorizationDecisionResponseAdapter(
        trust_result=make_trust(True),
        evidence_store=store,
    )

    current = time()

    result = adapter.authorize_and_prepare_response(
        actor_id="human-01",
        role=Role.ADMIN,
        action="approve_response",
        request_id="REQ-ADAPTER-BLOCK",
        authorization_id="AUTH-ADAPTER-BLOCK",
        nonce="nonce-adapter-block",
        risk_level="HIGH",
        reason="security test",
        target="test-target",
        issued_at=current,
        expires_at=current + 300,
    )

    assert result.authorized is False
    assert result.execution_allowed is False
    assert result.response_locked is True
    assert result.reason == "CANDIDATE_REQUIRED"


def test_req002_req005_adapter_plans_but_never_executes(
    tmp_path: Path,
):
    from time import time

    from guardian_hunter.authorization.contract import Role
    from guardian_hunter.authorization.decision_response_adapter import (
        AuthorizationDecisionResponseAdapter,
    )

    now = datetime.now(timezone.utc)

    store = EvidenceStore(
        tmp_path / "adapter-evidence.jsonl"
    )

    store.append(
        evidence_id="EV-ADAPTER-001",
        event_type="TEST",
        timestamp=now.timestamp(),
        payload={"status": "verified"},
    )

    candidate = Candidate(
        candidate_id="CAND-ADAPTER-001",
        evidence_id="EV-ADAPTER-001",
        created_at=now,
        expires_at=now + timedelta(minutes=10),
    )

    adapter = AuthorizationDecisionResponseAdapter(
        trust_result=make_trust(True),
        evidence_store=store,
    )

    current = time()

    result = adapter.authorize_and_prepare_response(
        actor_id="human-01",
        role=Role.ADMIN,
        action="approve_response",
        request_id="REQ-ADAPTER-VALID",
        authorization_id="AUTH-ADAPTER-VALID",
        nonce="nonce-adapter-valid",
        risk_level="HIGH",
        reason="security test",
        target="test-target",
        issued_at=current,
        expires_at=current + 300,
        candidate=candidate,
        approver="human-01",
        approval_reason="evidence reviewed",
    )

    assert result.authorized is True

    assert result.response_class is not None
    assert result.policy_decision is not None
    assert result.incident is not None

    # Defense in depth remains active.
    assert result.execution_allowed is False
    assert result.real_execution_blocked is True
    assert result.response_locked is True
    assert result.dry_run is True


def test_req001_response_without_trust_is_denied():
    from guardian_hunter.authorization.contract import (
        AuthorizationEngine,
        AuthorizationRequest,
        Identity,
        Permission,
        Role,
    )

    engine = AuthorizationEngine()

    decision = engine.authorize(
        Identity(
            actor_id="operator-01",
            role=Role.OPERATOR,
        ),
        AuthorizationRequest(
            request_id="REQ-NO-TRUST",
            authorization_id="AUTH-NO-TRUST",
            actor_id="operator-01",
            action=Permission.REQUEST_RESPONSE,
            nonce="nonce-no-trust",
            issued_at=100.0,
            expires_at=200.0,
            requires_human_review=True,
        ),
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.execution_allowed is False
    assert decision.response_locked is True
    assert "trust root required" in decision.reason


def test_req001_trust_denial_does_not_consume_nonce():
    from guardian_hunter.authorization.contract import (
        AuthorizationEngine,
        AuthorizationRequest,
        Identity,
        Permission,
        Role,
    )

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    request = AuthorizationRequest(
        request_id="REQ-TRUST-RETRY",
        authorization_id="AUTH-TRUST-RETRY",
        actor_id="operator-01",
        action=Permission.REQUEST_RESPONSE,
        nonce="nonce-trust-retry",
        issued_at=100.0,
        expires_at=200.0,
        requires_human_review=True,
    )

    no_trust = AuthorizationEngine()

    denied = no_trust.authorize(
        identity,
        request,
        now=150.0,
    )

    assert denied.authorized is False

    trusted = AuthorizationEngine(
        trust_result=make_trust(True)
    )

    approved = trusted.authorize(
        identity,
        request,
        now=150.0,
    )

    assert approved.authorized is True
    assert approved.execution_allowed is False
    assert approved.response_locked is True


def test_req001_trust_denial_does_not_reserve_nonce_same_engine():
    from guardian_hunter.authorization.contract import (
        AuthorizationEngine,
        AuthorizationRequest,
        Identity,
        Permission,
        Role,
    )

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    request = AuthorizationRequest(
        request_id="REQ-SAME-ENGINE",
        authorization_id="AUTH-SAME-ENGINE",
        actor_id="operator-01",
        action=Permission.REQUEST_RESPONSE,
        nonce="nonce-same-engine",
        issued_at=100.0,
        expires_at=200.0,
        requires_human_review=True,
    )

    engine = AuthorizationEngine()

    # First attempt fails only because Trust Root is absent.
    first = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert first.authorized is False
    assert "trust root required" in first.reason

    # Test-only injection to verify that the failed Trust attempt
    # did not consume the nonce in this SAME engine instance.
    engine._trust_result = make_trust(True)

    second = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert second.authorized is True
    assert second.execution_allowed is False
    assert second.real_execution_blocked is True
    assert second.response_locked is True


def test_repair_post_write_hash_mismatch_automatically_rolls_back(
    tmp_path: Path,
):
    """A failed post-write verification must never leave mutation behind."""
    from unittest.mock import patch

    import guardian_hunter.repair.executor as executor
    from guardian_hunter.repair.executor import (
        RepairAction,
        apply_repair,
    )
    from guardian_hunter.repair.proposal import RepairProposal
    from guardian_hunter.repair.approval import ApprovalLedger, approve

    target = tmp_path / "ordinary.txt"

    original = b"ORIGINAL\n"
    requested = b"REPLACEMENT\n"
    corrupted = b"CORRUPTED-WRITE\n"

    target.write_bytes(original)

    proposal = RepairProposal(
        finding_id="GH-1001",
        summary="Post-write mismatch rollback regression",
        affected_files=("ordinary.txt",),
        patch="controlled regression test",
        required_tests=("regression",),
    )

    action = RepairAction(
        relative_path="ordinary.txt",
        expected_sha256=executor._digest(original),
        replacement=requested,
    )

    # Test-scoped approval: never use a production ledger or approval.
    baseline = "a" * 40
    policy = {"test_scope": "isolated_rollback_regression", "version": 1}
    approval = approve(
        proposal,
        decision="APPROVED",
        approver_id="isolated-test-human",
        baseline=baseline,
        policy=policy,
    )
    ledger = ApprovalLedger(tmp_path / "approval-ledger.txt")

    real_atomic_replace_at = executor._atomic_replace_at
    calls = 0

    def corrupted_first_write(parent_fd, leaf, content):
        nonlocal calls
        calls += 1

        if calls == 1:
            return real_atomic_replace_at(
                parent_fd,
                leaf,
                corrupted,
            )

        return real_atomic_replace_at(
            parent_fd,
            leaf,
            content,
        )

    with patch.object(
        executor,
        "_atomic_replace_at",
        corrupted_first_write,
    ):
        result = apply_repair(
            root=tmp_path,
            proposal=proposal,
            action=action,
            baseline=baseline,
            approval=approval,
            approval_ledger=ledger,
            policy=policy,
        )

    assert calls == 2
    assert result.applied is False
    assert result.reason == "POST_WRITE_HASH_MISMATCH_ROLLED_BACK"
    assert target.read_bytes() == original
