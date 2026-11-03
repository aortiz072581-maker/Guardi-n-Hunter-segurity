"""Phase 81 — Defensive Monitoring Review."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveMonitoringReview:
    telemetry_ready: bool
    events_reconciled: bool
    observability_ready: bool
    audit_ready: bool
    response_locked: bool
    human_review_required: bool
    review_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_monitoring_review(
    telemetry_ready=True,
    events_reconciled=True,
    observability_ready=True,
    audit_ready=True,
    response_locked=True,
    human_review_required=True,
):
    review_valid = bool(
        telemetry_ready
        and events_reconciled
        and observability_ready
        and audit_ready
        and response_locked
        and human_review_required
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if review_valid else 0

    state = (
        "MONITORING_REVIEW_READY"
        if review_valid
        else "MONITORING_REVIEW_BLOCKED"
    )

    return DefensiveMonitoringReview(
        telemetry_ready=bool(telemetry_ready),
        events_reconciled=bool(events_reconciled),
        observability_ready=bool(observability_ready),
        audit_ready=bool(audit_ready),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        review_valid=review_valid,
        score=score,
        state=state,
    )


def monitoring_review_to_dict(record):
    return {
        "telemetry_ready": record.telemetry_ready,
        "events_reconciled": record.events_reconciled,
        "observability_ready": record.observability_ready,
        "audit_ready": record.audit_ready,
        "response_locked": record.response_locked,
        "human_review_required": record.human_review_required,
        "review_valid": record.review_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_monitoring_review(record):
    if not isinstance(record, DefensiveMonitoringReview):
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
