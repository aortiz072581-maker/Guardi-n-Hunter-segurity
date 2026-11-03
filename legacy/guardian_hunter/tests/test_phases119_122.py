"""Validation tests for phases 119 → 122."""

from guardian_hunter.governance.phase115_state_snapshot import (
    build_state_snapshot,
)
from guardian_hunter.verification.phase116_continuity import (
    validate_continuity,
)
from guardian_hunter.governance.phase117_safety_invariants import (
    validate_safety_invariants,
)
from guardian_hunter.verification.phase119_integrity_chain import (
    build_integrity_chain,
)
from guardian_hunter.governance.phase120_tamper_gate import (
    validate_tamper_gate,
)
from guardian_hunter.verification.phase121_safety_consistency import (
    validate_cross_phase_consistency,
)
from guardian_hunter.governance.phase122_release_gate import (
    build_release_continuity,
)


def test_phases_119_122():

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

    integrity = build_integrity_chain(
        snapshot_digest=snapshot.digest,
        state=snapshot.state,
        score=snapshot.score,
    )

    tamper_gate = validate_tamper_gate(
        integrity,
        tamper_detected=False,
        execution_blocked=True,
        human_review_required=True,
        response_locked=True,
    )

    consistency = validate_cross_phase_consistency(
        snapshot,
        continuity,
        safety,
        tamper_gate,
    )

    release = build_release_continuity(
        snapshot,
        integrity,
        tamper_gate,
        consistency,
    )

    assert integrity.valid is True
    assert integrity.score == 100
    assert len(integrity.chain_digest) == 64

    assert tamper_gate.clean is True
    assert tamper_gate.integrity_valid is True
    assert tamper_gate.tamper_detected is False
    assert tamper_gate.execution_blocked is True
    assert tamper_gate.human_review_required is True
    assert tamper_gate.response_locked is True
    assert tamper_gate.score == 100

    assert consistency.consistent is True
    assert consistency.snapshot_valid is True
    assert consistency.continuity_valid is True
    assert consistency.safety_valid is True
    assert consistency.tamper_gate_valid is True
    assert consistency.score == 100

    assert release.ready is True
    assert release.score == 100
    assert release.integrity_valid is True
    assert release.tamper_gate_valid is True
    assert release.cross_phase_consistent is True

    assert release.read_only is True
    assert release.dry_run is True
    assert release.real_execution_blocked is True
    assert release.human_review_required is True
    assert release.response_locked is True


if __name__ == "__main__":
    test_phases_119_122()

    print("==============================================================")
    print("119 → 122 MASTER VALIDATION: OK")
    print("STATE: DEFENSIVE_RELEASE_CONTINUITY_READY")
    print("SCORE: 100/100")
    print("INTEGRITY_CHAIN: VALID")
    print("TAMPER_GATE: CLEAN")
    print("CROSS_PHASE_CONSISTENCY: VALID")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL_EXECUTION_BLOCKED: TRUE")
    print("HUMAN_REVIEW_REQUIRED: TRUE")
    print("RESPONSE_LOCKED: TRUE")
    print("==============================================================")
