from guardian_hunter.governance.phase67_traceability import (
    build_traceability,
    validate_traceability,
)

from guardian_hunter.verification.phase68_recovery_continuity import (
    build_recovery_continuity,
    validate_recovery_continuity,
)

from guardian_hunter.governance.phase69_assurance import (
    build_assurance,
    validate_assurance,
)

from guardian_hunter.governance.phase70_closure import (
    build_operational_closure,
    validate_operational_closure,
)


def test_phase67():
    trace = build_traceability(
        event_count=5,
        source_links_valid=True,
        decision_links_valid=True,
        evidence_links_valid=True,
    )

    assert trace.traceability_valid is True
    assert trace.execution_blocked is True
    assert validate_traceability(trace) is True


def test_phase68():
    recovery = build_recovery_continuity(
        recovery_plan_valid=True,
        rollback_valid=True,
        verification_valid=True,
        recovery_documented=True,
    )

    assert recovery.continuity_valid is True
    assert recovery.human_review_required is True
    assert recovery.execution_blocked is True
    assert validate_recovery_continuity(recovery) is True


def test_phase69():
    assurance = build_assurance(
        True,
        True,
        True,
        True,
    )

    assert assurance.assurance_score == 100
    assert assurance.assurance_state == (
        "DEFENSIVE_ASSURANCE_READY"
    )
    assert assurance.response_locked is True
    assert validate_assurance(assurance) is True


def test_phase70():
    closure = build_operational_closure(
        True,
        True,
        True,
        True,
    )

    assert closure.closure_score == 100
    assert closure.closure_state == (
        "DEFENSIVE_OPERATIONAL_CLOSED"
    )
    assert closure.response_locked is True
    assert closure.final_review_required is True
    assert closure.execution_blocked is True
    assert validate_operational_closure(closure) is True


if __name__ == "__main__":
    test_phase67()
    test_phase68()
    test_phase69()
    test_phase70()

    print("PHASE 67: OK")
    print("PHASE 68: OK")
    print("PHASE 69: OK")
    print("PHASE 70: OK")
    print("67 → 70 TEST: OK")
