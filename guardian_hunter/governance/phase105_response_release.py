"""Phase 105 — Defensive Response System Release Review."""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseSystemRelease:
    score: int
    state: str
    release_valid: bool
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def build_response_system_release(
    score: int = 100,
    integrity_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseSystemRelease:

    score = max(0, min(100, int(score)))

    valid = (
        score == 100
        and integrity_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    return DefensiveResponseSystemRelease(
        score=score if valid else min(score, 99),
        state=(
            "DEFENSIVE_RESPONSE_SYSTEM_RELEASE_REVIEWED"
            if valid
            else "DEFENSIVE_RESPONSE_SYSTEM_RELEASE_HOLD"
        ),
        release_valid=valid,
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def release_to_dict(
    result: DefensiveResponseSystemRelease,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_system_release(
    result: DefensiveResponseSystemRelease,
) -> bool:
    return (
        isinstance(result, DefensiveResponseSystemRelease)
        and result.score == 100
        and result.state == "DEFENSIVE_RESPONSE_SYSTEM_RELEASE_REVIEWED"
        and result.release_valid is True
        and result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
