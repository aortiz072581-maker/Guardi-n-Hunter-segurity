from guardian_hunter.audit.authorization_hardening import (
    audit_safety_invariants,
    audit_engine_api,
    audit_unknown_action_fails_closed,
    audit_permission_boundaries,
    audit_inactive_identity,
    audit_actor_binding,
    audit_expiration,
    audit_replay_protection,
    audit_human_review_required,
    audit_execution_surface,
    audit_execution_gate,
)


def test_safety_invariants():
    audit_safety_invariants()


def test_engine_api():
    audit_engine_api()


def test_unknown_action_fails_closed():
    audit_unknown_action_fails_closed()


def test_permission_boundaries():
    audit_permission_boundaries()


def test_inactive_identity():
    audit_inactive_identity()


def test_actor_binding():
    audit_actor_binding()


def test_expiration():
    audit_expiration()


def test_replay_protection():
    audit_replay_protection()


def test_human_review_required():
    audit_human_review_required()


def test_execution_surface():
    audit_execution_surface()


def test_execution_gate():
    audit_execution_gate()
