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


def test_contract_runtime():
    ok, message = audit_contract_runtime()
    if not (ok):
    raise RuntimeError(message)


def test_decision_runtime():
    ok, message = audit_decision_runtime()
    if not (ok):
    raise RuntimeError(message)


def test_response_interfaces():
    ok, message = audit_response_interfaces()
    if not (ok):
    raise RuntimeError(message)


def test_all_target_modules_import():
    results = [audit_module(name) for name in TARGETS]

    if not (all(result.import_ok for result in results)):
    raise RuntimeError("Assertion failed: all(result.import_ok for result in results)")

    for result in results:
        if not (result.execution_allowed_true == 0):
        raise RuntimeError("Assertion failed: result.execution_allowed_true == 0")
        if not (result.forbidden_calls == ()):
        raise RuntimeError("Assertion failed: result.forbidden_calls == ()")


def test_authorization_parameters_exist_in_response_surface():
    policy = audit_module(
        "guardian_hunter.response.policy"
    )

    orchestrator = audit_module(
        "guardian_hunter.response.orchestrator"
    )

    if not (policy.authorized_parameters):
    raise RuntimeError("Assertion failed: policy.authorized_parameters")
    if not (orchestrator.authorized_parameters):
    raise RuntimeError("Assertion failed: orchestrator.authorized_parameters")


def test_authorization_modules_are_present():
    contract = audit_module(
        "guardian_hunter.authorization.contract"
    )

    bridge = audit_module(
        "guardian_hunter.authorization.phase18_bridge"
    )

    if not (contract.import_ok):
    raise RuntimeError("Assertion failed: contract.import_ok")
    if not (bridge.import_ok):
    raise RuntimeError("Assertion failed: bridge.import_ok")


def test_global_safety_audit():
    results = [audit_module(name) for name in TARGETS]

    ok, message = audit_safety(results)

    if not (ok):
    raise RuntimeError(message)
