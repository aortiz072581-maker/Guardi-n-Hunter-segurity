"""Phase 86 — Defensive Decision Continuity."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveDecisionContinuity:
    signal_ready: bool
    correlation_ready: bool
    decision_review_ready: bool
    risk_ready: bool
    response_locked: bool
    continuity_ready: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_decision_continuity(
    signal_ready=True,
    correlation_ready=True,
    decision_review_ready=True,
    risk_ready=True,
    response_locked=True,
):
    continuity_ready = bool(
        signal_ready
        and correlation_ready
        and decision_review_ready
        and risk_ready
        and response_locked
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if continuity_ready else 0

    state = (
        "DEFENSIVE_DECISION_CONTINUOUS"
        if continuity_ready
        else "DEFENSIVE_DECISION_BLOCKED"
    )

    return DefensiveDecisionContinuity(
        signal_ready=bool(signal_ready),
        correlation_ready=bool(correlation_ready),
        decision_review_ready=bool(decision_review_ready),
        risk_ready=bool(risk_ready),
        response_locked=bool(response_locked),
        continuity_ready=continuity_ready,
        score=score,
        state=state,
    )


def decision_continuity_to_dict(record):
    return {
        "signal_ready": record.signal_ready,
        "correlation_ready": record.correlation_ready,
        "decision_review_ready": record.decision_review_ready,
        "risk_ready": record.risk_ready,
        "response_locked": record.response_locked,
        "continuity_ready": record.continuity_ready,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_decision_continuity(record):
    if not isinstance(record, DefensiveDecisionContinuity):
        return False
    if record.score not in (0, 100):
        return False
    if record.continuity_ready and record.score != 100:
        return False
    if not record.response_locked:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    return True
