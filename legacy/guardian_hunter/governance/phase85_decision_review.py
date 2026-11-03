"""Phase 85 — Defensive Decision Review."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveDecisionReview:
    signals_ready: bool
    correlation_ready: bool
    risk_ready: bool
    decision_traceable: bool
    response_locked: bool
    human_review_required: bool
    review_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_decision_review(
    signals_ready=True,
    correlation_ready=True,
    risk_ready=True,
    decision_traceable=True,
    response_locked=True,
    human_review_required=True,
):
    review_valid = bool(
        signals_ready
        and correlation_ready
        and risk_ready
        and decision_traceable
        and response_locked
        and human_review_required
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if review_valid else 0

    state = (
        "DECISION_REVIEW_READY"
        if review_valid
        else "DECISION_REVIEW_BLOCKED"
    )

    return DefensiveDecisionReview(
        signals_ready=bool(signals_ready),
        correlation_ready=bool(correlation_ready),
        risk_ready=bool(risk_ready),
        decision_traceable=bool(decision_traceable),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        review_valid=review_valid,
        score=score,
        state=state,
    )


def decision_review_to_dict(record):
    return {
        "signals_ready": record.signals_ready,
        "correlation_ready": record.correlation_ready,
        "risk_ready": record.risk_ready,
        "decision_traceable": record.decision_traceable,
        "response_locked": record.response_locked,
        "human_review_required": record.human_review_required,
        "review_valid": record.review_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_decision_review(record):
    if not isinstance(record, DefensiveDecisionReview):
        return False
    if record.score not in (0, 100):
        return False
    if record.review_valid and record.score != 100:
        return False
    if not record.response_locked:
        return False
    if not record.human_review_required:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    return True
