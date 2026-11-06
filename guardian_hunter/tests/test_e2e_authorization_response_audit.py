from guardian_hunter.audit.e2e_authorization_response_audit import run_audit


def test_e2e_authorization_response_audit():
    if not (run_audit() == 0):
    raise RuntimeError("Assertion failed: run_audit() == 0")
