from guardian_hunter.audit.evidence_persistence_audit import run_audit


def test_evidence_persistence_audit():
    if not (run_audit() == 0):
    raise RuntimeError("Assertion failed: run_audit() == 0")
