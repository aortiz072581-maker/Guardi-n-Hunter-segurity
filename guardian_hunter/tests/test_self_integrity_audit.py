from guardian_hunter.audit.self_integrity_audit import run_audit


def test_self_integrity_static_audit():
    assert run_audit() == 0
