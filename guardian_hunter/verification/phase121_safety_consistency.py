"""Phase 121 — Cross-Phase Defensive Safety Consistency."""

from dataclasses import dataclass

from guardian_hunter.governance.phase115_state_snapshot import (
    StateSnapshot,
)
from guardian_hunter.verification.phase116_continuity import (
    ContinuityResult,
)
from guardian_hunter.governance.phase117_safety_invariants import (
    SafetyInvariantResult,
)
from guardian_hunter.governance.phase120_tamper_gate import (
    TamperGateResult,
)


@dataclass(frozen=True)
class SafetyConsistencyResult:
    state: str
    score: int
    consistent: bool
    snapshot_valid: bool
    continuity_valid: bool
    safety_valid: bool
    tamper_gate_valid: bool


def validate_cross_phase_consistency(
    snapshot: StateSnapshot,
    continuity: ContinuityResult,
    safety: SafetyInvariantResult,
    tamper_gate: TamperGateResult,
) -> SafetyConsistencyResult:

    snapshot_valid = (
        snapshot.read_only is True
        and snapshot.dry_run is True
        and snapshot.real_execution_blocked is True
        and snapshot.human_review_required is True
        and snapshot.response_locked is True
    )

    continuity_valid = continuity.continuous is True
    safety_valid = safety.invariants_valid is True
    tamper_gate_valid = tamper_gate.clean is True

    consistent = (
        snapshot_valid
        and continuity_valid
        and safety_valid
        and tamper_gate_valid
    )

    return SafetyConsistencyResult(
        state=(
            "DEFENSIVE_CROSS_PHASE_CONSISTENT"
            if consistent
            else "DEFENSIVE_CROSS_PHASE_BLOCKED"
        ),
        score=100 if consistent else 0,
        consistent=consistent,
        snapshot_valid=snapshot_valid,
        continuity_valid=continuity_valid,
        safety_valid=safety_valid,
        tamper_gate_valid=tamper_gate_valid,
    )
