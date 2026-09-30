"""Phase 117 — Immutable Safety Invariants."""

from dataclasses import dataclass

from guardian_hunter.governance.phase115_state_snapshot import (
    StateSnapshot,
)


@dataclass(frozen=True)
class SafetyInvariantResult:
    state: str
    score: int
    invariants_valid: bool
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool


def validate_safety_invariants(
    snapshot: StateSnapshot,
) -> SafetyInvariantResult:

    valid = (
        snapshot.read_only is True
        and snapshot.dry_run is True
        and snapshot.real_execution_blocked is True
        and snapshot.human_review_required is True
        and snapshot.response_locked is True
    )

    return SafetyInvariantResult(
        state=(
            "DEFENSIVE_SAFETY_INVARIANTS_VALID"
            if valid
            else "DEFENSIVE_SAFETY_INVARIANTS_BLOCKED"
        ),
        score=100 if valid else 0,
        invariants_valid=valid,
        read_only=snapshot.read_only,
        dry_run=snapshot.dry_run,
        real_execution_blocked=snapshot.real_execution_blocked,
        human_review_required=snapshot.human_review_required,
        response_locked=snapshot.response_locked,
    )
