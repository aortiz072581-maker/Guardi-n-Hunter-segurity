"""Phase 78 — Defensive Observability Readiness."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveObservabilityReadiness:
    baseline_ready: bool
    evidence_ready: bool
    alerts_ready: bool
    incident_review_ready: bool
    monitoring_ready: bool
    response_locked: bool
    observability_ready: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_observability_readiness(
    baseline_ready=True,
    evidence_ready=True,
    alerts_ready=True,
    incident_review_ready=True,
    monitoring_ready=True,
    response_locked=True,
):
    observability_ready = bool(
        baseline_ready
        and evidence_ready
        and alerts_ready
        and incident_review_ready
        and monitoring_ready
        and response_locked
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if observability_ready else 0

    state = (
        "DEFENSIVE_OBSERVABILITY_READY"
        if observability_ready
        else "DEFENSIVE_OBSERVABILITY_BLOCKED"
    )

    return DefensiveObservabilityReadiness(
        baseline_ready=bool(baseline_ready),
        evidence_ready=bool(evidence_ready),
        alerts_ready=bool(alerts_ready),
        incident_review_ready=bool(incident_review_ready),
        monitoring_ready=bool(monitoring_ready),
        response_locked=bool(response_locked),
        observability_ready=observability_ready,
        score=score,
        state=state,
    )


def observability_to_dict(record):
    return {
        "baseline_ready": record.baseline_ready,
        "evidence_ready": record.evidence_ready,
        "alerts_ready": record.alerts_ready,
        "incident_review_ready": record.incident_review_ready,
        "monitoring_ready": record.monitoring_ready,
        "response_locked": record.response_locked,
        "observability_ready": record.observability_ready,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_observability_readiness(record):
    if not isinstance(record, DefensiveObservabilityReadiness):
        return False
    if record.score not in (0, 100):
        return False
    if record.observability_ready and record.score != 100:
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
