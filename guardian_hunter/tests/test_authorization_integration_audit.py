"""Tests for Authorization → Decision/Response integration audit."""

from guardian_hunter.audit.authorization_integration_audit import (
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    HUMAN_REVIEW_REQUIRED,
    RESPONSE_LOCKED,
    audit_contract_runtime,
    audit_decision_runtime,
    audit_response_interfaces,
    audit_module,
    audit_safety,
    TARGETS,
)


def test_safety_invariants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def test_contract_runtime():
    ok, message = audit_contract_runtime()
    assert ok, message


def test_decision_runtime():
    ok, message = audit_decision_runtime()
    assert ok, message


def test_response_interfaces():
    ok, message = audit_response_interfaces()
    assert ok, message


def test_all_target_modules_import():
    results = [audit_module(name) for name in TARGETS]

    assert all(result.import_ok for result in results)

    for result in results:
        assert result.execution_allowed_true == 0
        assert result.forbidden_calls == ()


def test_authorization_parameters_exist_in_response_surface():
    policy = audit_module(
        "guardian_hunter.response.policy"
    )

    orchestrator = audit_module(
        "guardian_hunter.response.orchestrator"
    )

    assert policy.authorized_parameters
    assert orchestrator.authorized_parameters


def test_authorization_modules_are_present():
    contract = audit_module(
        "guardian_hunter.authorization.contract"
    )

    bridge = audit_module(
        "guardian_hunter.authorization.phase18_bridge"
    )

    assert contract.import_ok
    assert bridge.import_ok


def test_global_safety_audit():
    results = [audit_module(name) for name in TARGETS]

    ok, message = audit_safety(results)

    assert ok, message
