from guardian_hunter.audit.authorization_traceability_audit import run_audit


def test_authorization_traceability_audit():
    if not (run_audit() == 0):
    raise RuntimeError("Assertion failed: run_audit() == 0")
