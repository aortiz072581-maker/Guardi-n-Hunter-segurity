"""Phase 101 — Defensive Response Audit Assurance."""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseAudit:
    score: int
    state: str
    audit_valid: bool
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def build_response_audit(
    score: int = 100,
    evidence_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseAudit:

    score = max(0, min(100, int(score)))

    valid = (
        score == 100
        and evidence_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    return DefensiveResponseAudit(
        score=score if valid else min(score, 99),
        state=(
            "DEFENSIVE_RESPONSE_AUDIT_ASSURED"
            if valid
            else "DEFENSIVE_RESPONSE_AUDIT_HOLD"
        ),
        audit_valid=valid,
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def audit_to_dict(
    result: DefensiveResponseAudit,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_audit(
    result: DefensiveResponseAudit,
) -> bool:
    return (
        isinstance(result, DefensiveResponseAudit)
        and result.score == 100
        and result.state == "DEFENSIVE_RESPONSE_AUDIT_ASSURED"
        and result.audit_valid is True
        and result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
