from guardian_hunter.authorization.contract import (
    AuthorizationState,
    Permission,
    Role,
)
from guardian_hunter.authorization.phase18_bridge import (
    Phase18AuthorizationBridge,
    safety_invariants_hold,
)


def make_event(
    *,
    event_id="phase18-event-001",
    actor_id="operator-01",
    role="OPERATOR",
    action="request_response",
    nonce="phase18-nonce-001",
):
    return {
        "event_id": event_id,
        "actor_id": actor_id,
        "role": role,
        "action": action,
        "request_id": f"request-{event_id}",
        "authorization_id": f"authorization-{event_id}",
        "nonce": nonce,
        "issued_at": 100.0,
        "expires_at": 200.0,
        "identity_active": True,
    }


def test_phase18_bridge_authorizes_review_but_never_execution():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(),
        now=150.0,
    )

    assert result.authorized is True
    assert result.decision.state == AuthorizationState.APPROVED

    # HARD BLOCK
    assert result.execution_allowed is False
    assert result.decision.execution_allowed is False
    assert result.decision.real_execution_blocked is True


def test_phase18_bridge_preserves_five_safety_invariants():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-safety",
            nonce="phase18-safety-nonce",
        ),
        now=150.0,
    )

    assert result.decision.read_only is True
    assert result.decision.dry_run is True
    assert result.decision.real_execution_blocked is True
    assert result.decision.human_review_required is True
    assert result.decision.response_locked is True

    assert safety_invariants_hold() is True


def test_phase18_observer_cannot_request_response():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-observer",
            actor_id="observer-01",
            role="OBSERVER",
            action="request_response",
            nonce="observer-nonce",
        ),
        now=150.0,
    )

    assert result.authorized is False
    assert result.decision.execution_allowed is False
    assert result.decision.real_execution_blocked is True


def test_phase18_analyzer_can_analyze():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-analysis",
            actor_id="analyst-01",
            role="ANALYST",
            action="analyze",
            nonce="analysis-nonce",
        ),
        now=150.0,
    )

    assert result.authorized is True
    assert result.decision.execution_allowed is False


def test_phase18_invalid_role_fails_closed():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-invalid-role",
            role="UNKNOWN_ROLE",
            nonce="invalid-role-nonce",
        ),
        now=150.0,
    )

    assert result.authorized is False
    assert result.decision.state == AuthorizationState.INVALID
    assert result.decision.execution_allowed is False
    assert result.decision.real_execution_blocked is True


def test_phase18_missing_identity_fails_closed():
    bridge = Phase18AuthorizationBridge()

    event = make_event(
        event_id="phase18-missing-identity",
        nonce="missing-identity-nonce",
    )

    del event["actor_id"]

    result = bridge.authorize_phase18_event(
        event,
        now=150.0,
    )

    assert result.authorized is False
    assert result.decision.execution_allowed is False
    assert result.decision.real_execution_blocked is True


def test_phase18_replay_is_blocked():
    bridge = Phase18AuthorizationBridge()

    first = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-replay-001",
            nonce="same-phase18-nonce",
        ),
        now=150.0,
    )

    second = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-replay-002",
            nonce="same-phase18-nonce",
        ),
        now=150.0,
    )

    assert first.authorized is True
    assert second.authorized is False
    assert second.decision.state == AuthorizationState.REPLAYED

    assert second.decision.execution_allowed is False
    assert second.decision.real_execution_blocked is True


def test_phase18_audit_chain_remains_valid():
    bridge = Phase18AuthorizationBridge()

    bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-audit-001",
            nonce="audit-nonce-001",
        ),
        now=150.0,
    )

    bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-audit-002",
            nonce="audit-nonce-002",
        ),
        now=150.0,
    )

    assert bridge.engine.audit.verify() is True
    assert len(bridge.engine.audit.events) == 2


def test_no_bridge_path_can_enable_real_execution():
    bridge = Phase18AuthorizationBridge()

    roles_and_actions = [
        ("OBSERVER", "view"),
        ("ANALYST", "analyze"),
        ("OPERATOR", "request_response"),
        ("ADMIN", "approve_response"),
    ]

    for index, (role, action) in enumerate(
        roles_and_actions,
        start=1,
    ):
        result = bridge.authorize_phase18_event(
            make_event(
                event_id=f"phase18-role-{index}",
                actor_id=f"actor-{index}",
                role=role,
                action=action,
                nonce=f"role-nonce-{index}",
            ),
            now=150.0,
        )

        assert result.execution_allowed is False
        assert result.decision.execution_allowed is False
        assert result.decision.real_execution_blocked is True
        assert result.decision.read_only is True
        assert result.decision.dry_run is True
        assert result.decision.human_review_required is True
        assert result.decision.response_locked is True


def test_unknown_action_fails_closed():
    bridge = Phase18AuthorizationBridge()

    result = bridge.authorize_phase18_event(
        make_event(
            event_id="phase18-unknown-action",
            action="unknown-dangerous-action",
            nonce="unknown-action-nonce",
        ),
        now=150.0,
    )

    # Unknown action maps to REQUEST_RESPONSE and therefore requires
    # the corresponding role permission. OPERATOR has it, so the
    # authorization may be approved for review — but execution
    # remains hard blocked.
    assert result.decision.execution_allowed is False
    assert result.decision.real_execution_blocked is True
