from dataclasses import replace
from datetime import datetime, timezone

from guardian_hunter.security.trust_root import TrustResult
from guardian_hunter.authorization.contract import (
    AuthorizationEngine,
    AuthorizationState,
    Identity,
    Permission,
    Role,
)


def make_trusted_engine():
    """Test-only engine with synthetic verified trust."""
    trust = TrustResult(
        trusted=True,
        reason="TEST_TRUSTED",
        policy_id="POLICY-TEST",
        baseline_id="BASELINE-TEST",
        verification_time=datetime.now(
            timezone.utc
        ).isoformat(),
    )
    return AuthorizationEngine(trust_result=trust)


def make_request(
    request_id="req-001",
    authorization_id="auth-001",
    actor_id="operator-01",
    action=Permission.REQUEST_RESPONSE,
    nonce="nonce-001",
    issued_at=100.0,
    expires_at=200.0,
    requires_human_review=True,
):
    from guardian_hunter.authorization.contract import AuthorizationRequest

    return AuthorizationRequest(
        request_id=request_id,
        authorization_id=authorization_id,
        actor_id=actor_id,
        action=action,
        nonce=nonce,
        issued_at=issued_at,
        expires_at=expires_at,
        requires_human_review=requires_human_review,
    )


def test_valid_authorization_is_approved_but_execution_stays_blocked():
    engine = make_trusted_engine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    decision = engine.authorize(
        identity,
        make_request(),
        now=150.0,
    )

    assert decision.authorized is True
    assert decision.state == AuthorizationState.APPROVED
    assert decision.execution_allowed is False
    assert decision.real_execution_blocked is True
    assert decision.read_only is True
    assert decision.dry_run is True
    assert decision.human_review_required is True
    assert decision.response_locked is True


def test_missing_identity_fails_closed():
    engine = AuthorizationEngine()

    decision = engine.authorize(
        None,
        make_request(),
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.state == AuthorizationState.INVALID
    assert decision.execution_allowed is False


def test_identity_mismatch_is_denied():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    request = make_request(
        actor_id="operator-02",
    )

    decision = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.state == AuthorizationState.DENIED
    assert decision.execution_allowed is False


def test_observer_cannot_request_response():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="observer-01",
        role=Role.OBSERVER,
    )

    request = make_request(
        actor_id="observer-01",
        action=Permission.REQUEST_RESPONSE,
        nonce="observer-nonce",
    )

    decision = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.state == AuthorizationState.DENIED
    assert decision.execution_allowed is False


def test_human_review_is_mandatory():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    request = make_request(
        requires_human_review=False,
        nonce="no-review",
    )

    decision = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.state == AuthorizationState.DENIED
    assert decision.execution_allowed is False


def test_expired_authorization_is_denied():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    request = make_request(
        issued_at=100.0,
        expires_at=140.0,
        nonce="expired-nonce",
    )

    decision = engine.authorize(
        identity,
        request,
        now=150.0,
    )

    assert decision.authorized is False
    assert decision.state == AuthorizationState.EXPIRED
    assert decision.execution_allowed is False


def test_replay_is_denied():
    engine = make_trusted_engine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    first = engine.authorize(
        identity,
        make_request(
            request_id="req-001",
            authorization_id="auth-001",
            nonce="same-nonce",
        ),
        now=150.0,
    )

    second = engine.authorize(
        identity,
        make_request(
            request_id="req-002",
            authorization_id="auth-002",
            nonce="same-nonce",
        ),
        now=150.0,
    )

    assert first.authorized is True
    assert second.authorized is False
    assert second.state == AuthorizationState.REPLAYED
    assert second.execution_allowed is False


def test_same_nonce_with_new_request_is_still_replayed():
    engine = make_trusted_engine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    first = engine.authorize(
        identity,
        make_request(
            request_id="req-a",
            authorization_id="auth-a",
            nonce="nonce-fixed",
        ),
        now=150.0,
    )

    second = engine.authorize(
        identity,
        make_request(
            request_id="req-b",
            authorization_id="auth-b",
            nonce="nonce-fixed",
        ),
        now=150.0,
    )

    assert first.authorized is True
    assert second.authorized is False
    assert second.state == AuthorizationState.REPLAYED


def test_audit_chain_is_valid():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    engine.authorize(
        identity,
        make_request(
            request_id="req-001",
            authorization_id="auth-001",
            nonce="nonce-001",
        ),
        now=150.0,
    )

    engine.authorize(
        identity,
        make_request(
            request_id="req-002",
            authorization_id="auth-002",
            nonce="nonce-002",
        ),
        now=150.0,
    )

    assert len(engine.audit.events) == 2
    assert engine.audit.verify() is True


def test_audit_tampering_is_detected():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    engine.authorize(
        identity,
        make_request(),
        now=150.0,
    )

    assert engine.audit.verify() is True

    event = engine.audit.events[0]

    engine.audit.events[0] = replace(
        event,
        actor_id="tampered",
    )

    assert engine.audit.verify() is False


def test_all_roles_can_never_enable_real_execution():
    engine = AuthorizationEngine()

    actions = {
        Role.OBSERVER: Permission.VIEW,
        Role.ANALYST: Permission.ANALYZE,
        Role.OPERATOR: Permission.REQUEST_RESPONSE,
        Role.ADMIN: Permission.APPROVE_RESPONSE,
    }

    for index, (role, action) in enumerate(actions.items(), start=1):
        identity = Identity(
            actor_id=f"actor-{index}",
            role=role,
        )

        request = make_request(
            request_id=f"req-role-{index}",
            authorization_id=f"auth-role-{index}",
            actor_id=f"actor-{index}",
            action=action,
            nonce=f"role-nonce-{index}",
        )

        decision = engine.authorize(
            identity,
            request,
            now=150.0,
        )

        assert decision.execution_allowed is False
        assert decision.real_execution_blocked is True
        assert decision.read_only is True
        assert decision.dry_run is True
        assert decision.human_review_required is True
        assert decision.response_locked is True


def test_safety_invariants_are_always_present():
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-01",
        role=Role.OPERATOR,
    )

    decision = engine.authorize(
        identity,
        make_request(),
        now=150.0,
    )

    assert decision.execution_allowed is False
    assert decision.real_execution_blocked is True
    assert decision.read_only is True
    assert decision.dry_run is True
    assert decision.human_review_required is True
    assert decision.response_locked is True
