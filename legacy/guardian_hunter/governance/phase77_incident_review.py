"""Phase 77 — Defensive Incident Review Gate."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveIncidentReview:
    incident_present: bool
    evidence_ready: bool
    alerts_reconciled: bool
    audit_ready: bool
    response_locked: bool
    human_review_required: bool
    review_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_incident_review(
    incident_present=False,
    evidence_ready=True,
    alerts_reconciled=True,
    audit_ready=True,
    response_locked=True,
    human_review_required=True,
):
    review_valid = bool(
        evidence_ready
        and alerts_reconciled
        and audit_ready
        and response_locked
        and human_review_required
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if review_valid else 0

    state = (
        "INCIDENT_REVIEW_READY"
        if review_valid
        else "INCIDENT_REVIEW_BLOCKED"
    )

    return DefensiveIncidentReview(
        incident_present=bool(incident_present),
        evidence_ready=bool(evidence_ready),
        alerts_reconciled=bool(alerts_reconciled),
        audit_ready=bool(audit_ready),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        review_valid=review_valid,
        score=score,
        state=state,
    )


def incident_review_to_dict(record):
    return {
        "incident_present": record.incident_present,
        "evidence_ready": record.evidence_ready,
        "alerts_reconciled": record.alerts_reconciled,
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


def validate_incident_review(record):
    if not isinstance(record, DefensiveIncidentReview):
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
