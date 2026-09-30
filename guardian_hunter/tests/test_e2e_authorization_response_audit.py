from guardian_hunter.audit.e2e_authorization_response_audit import run_audit


def test_e2e_authorization_response_audit():
    assert run_audit() == 0
