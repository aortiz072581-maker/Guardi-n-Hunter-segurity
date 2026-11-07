from guardian_hunter.audit.authorization_traceability_audit import run_audit


def test_authorization_traceability_audit():
    assert run_audit() == 0
