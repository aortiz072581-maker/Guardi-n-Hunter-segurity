"""Phase 109 — Defensive Response System Final Review."""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseFinalReview:
    score: int
    state: str
    review_valid: bool
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def build_response_final_review(
    score: int = 100,
    traceability_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseFinalReview:

    score = max(0, min(100, int(score)))

    valid = (
        score == 100
        and traceability_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    return DefensiveResponseFinalReview(
        score=score if valid else min(score, 99),
        state=(
            "DEFENSIVE_RESPONSE_FINAL_REVIEW_VALID"
            if valid
            else "DEFENSIVE_RESPONSE_FINAL_REVIEW_HOLD"
        ),
        review_valid=valid,
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def review_to_dict(
    result: DefensiveResponseFinalReview,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_final_review(
    result: DefensiveResponseFinalReview,
) -> bool:
    return (
        isinstance(result, DefensiveResponseFinalReview)
        and result.score == 100
        and result.state == "DEFENSIVE_RESPONSE_FINAL_REVIEW_VALID"
        and result.review_valid is True
        and result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
