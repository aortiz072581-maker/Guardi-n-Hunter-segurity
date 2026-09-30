from guardian_hunter.audit.phase18_interface_audit import (
    PHASE18_MODULES,
    inspect_bridge,
    inspect_phase18_interfaces,
    inspect_safety_invariants,
    scan_forbidden_execution_patterns,
)


def test_all_phase18_modules_have_real_interfaces():
    records = inspect_phase18_interfaces()

    assert len(records) == len(PHASE18_MODULES)
    assert all(record.imports_ok for record in records)


def test_phase18_bridge_is_available():
    ok, issues = inspect_bridge()

    assert ok is True, issues


def test_no_forbidden_execution_patterns_exist():
    findings = scan_forbidden_execution_patterns()

    assert findings == ()


def test_authorization_safety_invariants_hold():
    assert inspect_safety_invariants() is True
