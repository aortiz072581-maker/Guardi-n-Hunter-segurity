from guardian_hunter.governance.phase55_evidence_continuity import (
    build_evidence_continuity,
    validate_evidence_continuity,
)

from guardian_hunter.verification.phase56_alert_continuity import (
    build_alert_continuity,
    validate_alert_continuity,
)

from guardian_hunter.governance.phase57_recovery_gate import (
    build_recovery_gate,
    validate_recovery_gate,
)

from guardian_hunter.governance.phase58_operational_readiness import (
    build_operational_readiness,
    validate_operational_readiness,
)


def test_phase55():
    record = build_evidence_continuity(
        evidence_count=3,
        evidence_integrity=True,
        chain_integrity=True,
    )

    assert record.evidence_preserved is True
    assert record.continuity_valid is True
    assert validate_evidence_continuity(record) is True


def test_phase56():
    record = build_alert_continuity(
        alert_count=4,
        alerts_valid=True,
        correlation_valid=True,
    )

    assert record.alerts_preserved is True
    assert record.continuity_valid is True
    assert validate_alert_continuity(record) is True


def test_phase57():
    gate = build_recovery_gate(
        True,
        True,
        True,
        True,
    )

    assert gate.recovery_allowed is True
    assert gate.human_review_required is True
    assert gate.execution_blocked is True
    assert validate_recovery_gate(gate) is True


def test_phase58():
    readiness = build_operational_readiness(
        True,
        True,
        True,
        True,
        True,
    )

    assert readiness.readiness_score == 100
    assert readiness.readiness_state == (
        "OPERATIONAL_DEFENSIVE_READY"
    )
    assert readiness.execution_blocked is True
    assert validate_operational_readiness(readiness) is True


if __name__ == "__main__":
    test_phase55()
    test_phase56()
    test_phase57()
    test_phase58()

    print("PHASE 55: OK")
    print("PHASE 56: OK")
    print("PHASE 57: OK")
    print("PHASE 58: OK")
    print("55 → 58 TEST: OK")
