from guardian_hunter.audit.incident_state_recovery_audit import run_audit


def test_incident_state_recovery_audit():
    assert run_audit() == 0
