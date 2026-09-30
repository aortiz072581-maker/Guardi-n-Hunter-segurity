"""Tests for the controlled Authorization → Decision/Response adapter."""

from time import time

from guardian_hunter.authorization.contract import Role

from guardian_hunter.authorization.decision_response_adapter import (
    AuthorizationDecisionResponseAdapter,
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    HUMAN_REVIEW_REQUIRED,
    RESPONSE_LOCKED,
)


def make_adapter():
    return AuthorizationDecisionResponseAdapter()


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

    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True
    assert adapter.safety_invariants_hold() is True


def test_authorized_request_prepares_response_only():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    assert result.authorized is True
    assert result.execution_allowed is False
    assert result.real_execution_blocked is True
    assert result.human_review_required is True
    assert result.response_locked is True
    assert result.response_class is not None
    assert result.policy_decision is not None
    assert result.incident is not None


def test_unknown_action_fails_closed():
    adapter = make_adapter()

    data = valid_kwargs()
    data["action"] = "unknown_action"
    data["nonce"] = "unknown-action-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is False
    assert result.execution_allowed is False
    assert result.response_class is None
    assert result.policy_decision is None
    assert result.incident is None
    assert "UNKNOWN_ACTION_FAIL_CLOSED" in result.reason


def test_observer_cannot_request_response():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.OBSERVER
    data["nonce"] = "observer-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is False
    assert result.execution_allowed is False


def test_analyst_cannot_request_response():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.ANALYST
    data["nonce"] = "analyst-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is False
    assert result.execution_allowed is False


def test_operator_can_request_response():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.OPERATOR
    data["nonce"] = "operator-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is True
    assert result.execution_allowed is False


def test_expired_request_fails_closed():
    adapter = make_adapter()

    data = valid_kwargs()
    now = time()

    data["issued_at"] = now - 120
    data["expires_at"] = now - 60
    data["nonce"] = "expired-request-nonce"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is False
    assert result.execution_allowed is False


def test_replay_fails_closed():
    adapter = make_adapter()

    data = valid_kwargs()
    data["nonce"] = "replay-protection-nonce"

    first = adapter.authorize_and_prepare_response(**data)
    second = adapter.authorize_and_prepare_response(**data)

    assert first.authorized is True
    assert first.execution_allowed is False

    assert second.authorized is False
    assert second.execution_allowed is False


def test_human_review_is_mandatory():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    assert result.human_review_required is True
    assert result.response_locked is True


def test_authorization_never_grants_execution():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    assert result.execution_allowed is False
    assert result.real_execution_blocked is True


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

    assert mutated is False
    assert result.execution_allowed is False


def test_response_planning_requires_authorization():
    adapter = make_adapter()

    data = valid_kwargs()
    data["role"] = Role.OBSERVER
    data["nonce"] = "blocked-before-response"

    result = adapter.authorize_and_prepare_response(**data)

    assert result.authorized is False
    assert result.response_class is None
    assert result.policy_decision is None
    assert result.incident is None


def test_final_safety_state():
    adapter = make_adapter()

    result = adapter.authorize_and_prepare_response(
        **valid_kwargs()
    )

    assert result.read_only is True
    assert result.dry_run is True
    assert result.real_execution_blocked is True
    assert result.human_review_required is True
    assert result.response_locked is True
    assert result.execution_allowed is False
