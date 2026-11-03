"""Validation tests for phases 115 → 118."""

from guardian_hunter.governance.phase115_state_snapshot import (
    build_state_snapshot,
)
from guardian_hunter.verification.phase116_continuity import (
    validate_continuity,
)
from guardian_hunter.governance.phase117_safety_invariants import (
    validate_safety_invariants,
)
from guardian_hunter.governance.phase118_master_gate import (
    build_master_validation,
)


def test_phases_115_118():

    snapshot = build_state_snapshot(
        state="DEFENSIVE_RESPONSE_RELEASE_GATE_READY",
        score=100,
        read_only=True,
        dry_run=True,
        real_execution_blocked=True,
        human_review_required=True,
        response_locked=True,
    )

    continuity = validate_continuity(snapshot)

    safety = validate_safety_invariants(snapshot)

    master = build_master_validation(
        snapshot,
        continuity,
        safety,
    )

    assert snapshot.digest
    assert snapshot.score == 100

    assert continuity.continuous is True
    assert continuity.previous_state_valid is True
    assert continuity.safety_flags_valid is True
    assert continuity.score == 100

    assert safety.invariants_valid is True
    assert safety.read_only is True
    assert safety.dry_run is True
    assert safety.real_execution_blocked is True
    assert safety.human_review_required is True
    assert safety.response_locked is True
    assert safety.score == 100

    assert master.release_ready is True
    assert master.continuity_valid is True
    assert master.safety_invariants_valid is True
    assert master.score == 100
    assert master.state == "DEFENSIVE_MASTER_VALIDATION_READY"

    assert master.read_only is True
    assert master.dry_run is True
    assert master.real_execution_blocked is True
    assert master.human_review_required is True
    assert master.response_locked is True


if __name__ == "__main__":
    test_phases_115_118()

    print("==============================================================")
    print("115 → 118 MASTER VALIDATION: OK")
    print("STATE: DEFENSIVE_MASTER_VALIDATION_READY")
    print("SCORE: 100/100")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL_EXECUTION_BLOCKED: TRUE")
    print("HUMAN_REVIEW_REQUIRED: TRUE")
    print("RESPONSE_LOCKED: TRUE")
    print("==============================================================")
