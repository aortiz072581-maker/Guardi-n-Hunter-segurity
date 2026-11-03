"""Phase 89 — Defensive Response Assurance
Read-only assurance gate before any human-reviewed response.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseAssurance:
    score: int
    state: str
    assurance_valid: bool
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def build_response_assurance(
    score: int = 100,
    integrity_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseAssurance:

    score = max(0, min(100, int(score)))

    assurance_valid = (
        score == 100
        and integrity_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    return DefensiveResponseAssurance(
        score=score if assurance_valid else min(score, 99),
        state=(
            "DEFENSIVE_RESPONSE_ASSURED"
            if assurance_valid
            else "DEFENSIVE_RESPONSE_ASSURANCE_HOLD"
        ),
        assurance_valid=assurance_valid,
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def assurance_to_dict(
    assurance: DefensiveResponseAssurance,
) -> Dict[str, Any]:
    return asdict(assurance)


def validate_response_assurance(
    assurance: DefensiveResponseAssurance,
) -> bool:
    return (
        isinstance(assurance, DefensiveResponseAssurance)
        and 0 <= assurance.score <= 100
        and assurance.state == "DEFENSIVE_RESPONSE_ASSURED"
        and assurance.assurance_valid is True
        and assurance.response_locked is True
        and assurance.human_review_required is True
        and assurance.read_only is True
        and assurance.dry_run is True
        and assurance.execution_allowed is False
    )
