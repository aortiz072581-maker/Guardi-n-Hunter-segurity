"""Phase 118 — Master Defensive Validation Gate."""

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


@dataclass(frozen=True)
class MasterValidationResult:
    state: str
    score: int
    release_ready: bool
    continuity_valid: bool
    safety_invariants_valid: bool
    human_review_required: bool
    response_locked: bool
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool


def build_master_validation(
    snapshot: StateSnapshot,
    continuity: ContinuityResult,
    safety: SafetyInvariantResult,
) -> MasterValidationResult:

    release_ready = (
        snapshot.score >= 100
        and continuity.score >= 100
        and safety.score >= 100
        and continuity.continuous is True
        and safety.invariants_valid is True
        and snapshot.read_only is True
        and snapshot.dry_run is True
        and snapshot.real_execution_blocked is True
        and snapshot.human_review_required is True
        and snapshot.response_locked is True
    )

    return MasterValidationResult(
        state=(
            "DEFENSIVE_MASTER_VALIDATION_READY"
            if release_ready
            else "DEFENSIVE_MASTER_VALIDATION_BLOCKED"
        ),
        score=100 if release_ready else 0,
        release_ready=release_ready,
        continuity_valid=continuity.continuous,
        safety_invariants_valid=safety.invariants_valid,
        human_review_required=snapshot.human_review_required,
        response_locked=snapshot.response_locked,
        read_only=snapshot.read_only,
        dry_run=snapshot.dry_run,
        real_execution_blocked=snapshot.real_execution_blocked,
    )
