"""Phase 74 — Defensive Monitoring Readiness.

Final read-only readiness gate for defensive monitoring.
Does not enable response execution.
"""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveMonitoringReadiness:
    baseline_ready: bool
    integrity_ready: bool
    review_ready: bool
    response_locked: bool
    monitoring_ready: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_monitoring_readiness(
    baseline_ready=True,
    integrity_ready=True,
    review_ready=True,
    response_locked=True,
):
    monitoring_ready = bool(
        baseline_ready
        and integrity_ready
        and review_ready
        and response_locked
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if monitoring_ready else 0

    state = (
        "DEFENSIVE_MONITORING_READY"
        if monitoring_ready
        else "DEFENSIVE_MONITORING_BLOCKED"
    )

    return DefensiveMonitoringReadiness(
        baseline_ready=bool(baseline_ready),
        integrity_ready=bool(integrity_ready),
        review_ready=bool(review_ready),
        response_locked=bool(response_locked),
        monitoring_ready=monitoring_ready,
        score=score,
        state=state,
    )


def monitoring_readiness_to_dict(record):
    return {
        "baseline_ready": record.baseline_ready,
        "integrity_ready": record.integrity_ready,
        "review_ready": record.review_ready,
        "response_locked": record.response_locked,
        "monitoring_ready": record.monitoring_ready,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_monitoring_readiness(record):
    if not isinstance(record, DefensiveMonitoringReadiness):
        return False
    if record.score not in (0, 100):
        return False
    if record.monitoring_ready and record.score != 100:
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
