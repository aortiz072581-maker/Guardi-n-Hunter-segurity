from guardian_hunter.audit.tamper_detection_audit import run_audit


def test_tamper_detection_audit():
    assert run_audit() == 0
