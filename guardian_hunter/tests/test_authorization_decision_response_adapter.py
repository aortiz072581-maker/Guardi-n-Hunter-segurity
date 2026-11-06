"""Tests for the controlled Authorization → Decision/Response adapter."""

from time import time
from datetime import datetime, timedelta, timezone

from guardian_hunter.authorization.contract import Role
from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.security.mode import Candidate
from guardian_hunter.security.trust_root import TrustResult

from guardian_hunter.authorization.decision_response_adapter import (
    AuthorizationDecisionResponseAdapter,
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    HUMAN_REVIEW_REQUIRED,
    RESPONSE_LOCKED,
)


def make_adapter(tmp_path=None):
    # Negative/legacy tests keep the default fail-closed adapter.
    if tmp_path is None:
        return AuthorizationDecisionResponseAdapter()

    trust = TrustResult(
        trusted=True,
        reason="TEST_TRUSTED",
        policy_id="TEST_POLICY",
        baseline_id="TEST_BASELINE",
        verification_time=datetime.now(timezone.utc).isoformat(),
    )

    evidence_store = EvidenceStore(tmp_path / "adapter-evidence.jsonl")

    evidence_id = "adapter-test-evidence"
    evidence_store.append(
        evidence_id=evidence_id,
        event_type="ADAPTER_TEST",
        timestamp=time(),
        payload={"test": True},
    )

    adapter = AuthorizationDecisionResponseAdapter(
        trust_result=trust,
        evidence_store=evidence_store,
    )

    now = datetime.now(timezone.utc)
    candidate = Candidate(
        candidate_id="adapter-test-candidate",
        evidence_id=evidence_id,
        created_at=now - timedelta(seconds=1),
        expires_at=now + timedelta(minutes=5),
    )

    return adapter, candidate


def valid_kwargs():
    now = time()

    return {
        "actor_id": "adapter-test-actor",
        "role": Role.ADMIN,
        "action": "request_response",
        "request_id": "adapter-test-request",
        "authorization_id": "adapter-test-auth",
        "nonce": "adapter-test-nonce",
        "risk_level": "HIGH",
        "reason": "controlled defensive test",
        "target": "test-target",
        "risk_data": {"test": True},
        "issued_at": now - 1,
        "expires_at": now + 60,
    }


def test_safety_invariants():
    adapter = make_adapter()

    if not (READ_ONLY is True):
    raise RuntimeError("Assertion failed: READ_ONLY is True")
    if not (DRY_RUN is True):
    raise RuntimeError("Assertion failed: DRY_RUN is True")
    if not (REAL_EXECUTION_BLOCKED is True):
    raise RuntimeError("Assertion failed: REAL_EXECUTION_BLOCKED is True")
    if not (HUMAN_REVIEW_REQUIRED is True):
    raise RuntimeError("Assertion failed: HUMAN_REVIEW_REQUIRED is True")
    if not (RESPONSE_LOCKED is True):
    raise RuntimeError("Assertion failed: RESPONSE_LOCKED is True")
    if not (adapter.safety_invariants_hold() is True):
    raise RuntimeError("Assertion failed: adapter.safety_invariants_hold() is True")


def test_authorized_request_prepares_response_only(tmp_path):
    adapter, candidate = make_adapter(tmp_path)

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs(),
        candidate=candidate,
        approver="adapter-test-approver",
        approval_reason="controlled test approval",
    )

    if not (result.authorized is True):
    raise RuntimeError("Assertion failed: result.authorized is True")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")
    if not (result.real_execution_blocked is True):
    raise RuntimeError("Assertion failed: result.real_execution_blocked is True")
    if not (result.human_review_required is True):
    raise RuntimeError("Assertion failed: result.human_review_required is True")
    if not (result.response_locked is True):
    raise RuntimeError("Assertion failed: result.response_locked is True")
    if not (result.response_class is not None):
    raise RuntimeError("Assertion failed: result.response_class is not None")
    if not (result.policy_decision is not None):
    raise RuntimeError("Assertion failed: result.policy_decision is not None")
    if not (result.incident is not None):
    raise RuntimeError("Assertion failed: result.incident is not None")


def test_unknown_action_fails_closed():
    adapter = make_adapter()

    data = valid_kwargs()
    data["action"] = "unknown_action"
    data["nonce"] = "unknown-action-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    if not (result.authorized is False):
    raise RuntimeError("Assertion failed: result.authorized is False")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")
    if not (result.response_class is None):
    raise RuntimeError("Assertion failed: result.response_class is None")
    if not (result.policy_decision is None):
    raise RuntimeError("Assertion failed: result.policy_decision is None")
    if not (result.incident is None):
    raise RuntimeError("Assertion failed: result.incident is None")
    if not ("UNKNOWN_ACTION_FAIL_CLOSED" in result.reason):
    raise RuntimeError("Assertion failed: "UNKNOWN_ACTION_FAIL_CLOSED" in result.reason")


def test_observer_cannot_request_response():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.OBSERVER
    data["nonce"] = "observer-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    if not (result.authorized is False):
    raise RuntimeError("Assertion failed: result.authorized is False")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")


def test_analyst_cannot_request_response():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.ANALYST
    data["nonce"] = "analyst-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    if not (result.authorized is False):
    raise RuntimeError("Assertion failed: result.authorized is False")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")


def test_operator_can_request_response(tmp_path):
    adapter, candidate = make_adapter(tmp_path)

    data = valid_kwargs()
    data["role"] = Role.OPERATOR
    data["nonce"] = "operator-request-nonce"

    result = adapter.authorize_and_prepare_response(
        **data,
        candidate=candidate,
        approver="adapter-test-approver",
        approval_reason="controlled operator test approval",
    )

    if not (result.authorized is True):
    raise RuntimeError("Assertion failed: result.authorized is True")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")


def test_expired_request_fails_closed():
    adapter = make_adapter()

    data = valid_kwargs()
    now = time()

    data["issued_at"] = now - 120
    data["expires_at"] = now - 60
    data["nonce"] = "expired-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    if not (result.authorized is False):
    raise RuntimeError("Assertion failed: result.authorized is False")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")


def test_replay_fails_closed(tmp_path):
    adapter, candidate = make_adapter(tmp_path)

    data = valid_kwargs()
    data["nonce"] = "replay-protection-nonce"

    candidate_kwargs = {
        "candidate": candidate,
        "approver": "adapter-test-approver",
        "approval_reason": "controlled replay test approval",
    }

    first = adapter.authorize_and_prepare_response(
        **data,
        **candidate_kwargs,
    )
    second = adapter.authorize_and_prepare_response(
        **data,
        **candidate_kwargs,
    )

    if not (first.authorized is True):
    raise RuntimeError("Assertion failed: first.authorized is True")
    if not (first.execution_allowed is False):
    raise RuntimeError("Assertion failed: first.execution_allowed is False")

    if not (second.authorized is False):
    raise RuntimeError("Assertion failed: second.authorized is False")
    if not (second.execution_allowed is False):
    raise RuntimeError("Assertion failed: second.execution_allowed is False")


def test_human_review_is_mandatory():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    if not (result.human_review_required is True):
    raise RuntimeError("Assertion failed: result.human_review_required is True")
    if not (result.response_locked is True):
    raise RuntimeError("Assertion failed: result.response_locked is True")


def test_authorization_never_grants_execution():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")
    if not (result.real_execution_blocked is True):
    raise RuntimeError("Assertion failed: result.real_execution_blocked is True")


def test_adapter_result_is_immutable():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    mutated = False

    try:
        result.execution_allowed = True
        mutated = True
    except Exception:
        mutated = False

    if not (mutated is False):
    raise RuntimeError("Assertion failed: mutated is False")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")


def test_response_planning_requires_authorization():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.OBSERVER
    data["nonce"] = "blocked-before-response"

    result = adapter.authorize_and_prepare_response(**data)

    if not (result.authorized is False):
    raise RuntimeError("Assertion failed: result.authorized is False")
    if not (result.response_class is None):
    raise RuntimeError("Assertion failed: result.response_class is None")
    if not (result.policy_decision is None):
    raise RuntimeError("Assertion failed: result.policy_decision is None")
    if not (result.incident is None):
    raise RuntimeError("Assertion failed: result.incident is None")


def test_final_safety_state():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    if not (result.read_only is True):
    raise RuntimeError("Assertion failed: result.read_only is True")
    if not (result.dry_run is True):
    raise RuntimeError("Assertion failed: result.dry_run is True")
    if not (result.real_execution_blocked is True):
    raise RuntimeError("Assertion failed: result.real_execution_blocked is True")
    if not (result.human_review_required is True):
    raise RuntimeError("Assertion failed: result.human_review_required is True")
    if not (result.response_locked is True):
    raise RuntimeError("Assertion failed: result.response_locked is True")
    if not (result.execution_allowed is False):
    raise RuntimeError("Assertion failed: result.execution_allowed is False")
