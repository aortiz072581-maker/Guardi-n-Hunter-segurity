from guardian_hunter.audit.evidence_persistence_audit import run_audit


def test_evidence_persistence_audit():
    assert run_audit() == 0
