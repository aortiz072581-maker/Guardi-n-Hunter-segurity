"""Phase 87 — Defensive Response Review
Read-only defensive governance layer.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseReview:
    score: int
    state: str
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def build_response_review(
    score: int = 100,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseReview:
    score = max(0, min(100, int(score)))

    return DefensiveResponseReview(
        score=score,
        state="DEFENSIVE_RESPONSE_REVIEWED",
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def response_review_to_dict(
    review: DefensiveResponseReview,
) -> Dict[str, Any]:
    return asdict(review)


def validate_response_review(
    review: DefensiveResponseReview,
) -> bool:
    return (
        isinstance(review, DefensiveResponseReview)
        and 0 <= review.score <= 100
        and review.state == "DEFENSIVE_RESPONSE_REVIEWED"
        and review.response_locked is True
        and review.human_review_required is True
        and review.read_only is True
        and review.dry_run is True
        and review.execution_allowed is False
    )
