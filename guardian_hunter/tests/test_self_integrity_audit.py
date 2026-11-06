from guardian_hunter.audit.self_integrity_audit import run_audit


def test_self_integrity_static_audit():
    if not (run_audit() == 0):
    raise RuntimeError("Assertion failed: run_audit() == 0")
