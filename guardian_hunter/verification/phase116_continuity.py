"""Phase 116 — Defensive Response Continuity Validation."""

from dataclasses import dataclass

from guardian_hunter.governance.phase115_state_snapshot import (
    StateSnapshot,
)


EXPECTED_PREVIOUS_STATE = "DEFENSIVE_RESPONSE_RELEASE_GATE_READY"


@dataclass(frozen=True)
class ContinuityResult:
    state: str
    score: int
    continuous: bool
    previous_state_valid: bool
    safety_flags_valid: bool
    human_review_required: bool
    response_locked: bool


def validate_continuity(
    snapshot: StateSnapshot,
    *,
    expected_previous_state: str = EXPECTED_PREVIOUS_STATE,
) -> ContinuityResult:

    previous_state_valid = (
        snapshot.state == expected_previous_state
    )

    safety_flags_valid = (
        snapshot.read_only is True
        and snapshot.dry_run is True
        and snapshot.real_execution_blocked is True
        and snapshot.human_review_required is True
        and snapshot.response_locked is True
    )

    continuous = (
        previous_state_valid
        and safety_flags_valid
        and snapshot.score >= 100
    )

    return ContinuityResult(
        state=(
            "DEFENSIVE_RESPONSE_CONTINUITY_VALID"
            if continuous
            else "DEFENSIVE_RESPONSE_CONTINUITY_BLOCKED"
        ),
        score=100 if continuous else 0,
        continuous=continuous,
        previous_state_valid=previous_state_valid,
        safety_flags_valid=safety_flags_valid,
        human_review_required=snapshot.human_review_required,
        response_locked=snapshot.response_locked,
    )
