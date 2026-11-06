from guardian_hunter.audit.tamper_detection_audit import run_audit


def test_tamper_detection_audit():
    if not (run_audit() == 0):
    raise RuntimeError("Assertion failed: run_audit() == 0")
