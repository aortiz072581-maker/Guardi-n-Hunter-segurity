"""Phase 73 — Defensive Final Review Gate.

Human-review gate before operational monitoring.
Never authorizes real execution.
"""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveFinalReview:
    baseline_ok: bool
    integrity_ok: bool
    audit_ok: bool
    response_locked: bool
    human_review_required: bool
    review_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_final_review(
    baseline_ok=True,
    integrity_ok=True,
    audit_ok=True,
    response_locked=True,
    human_review_required=True,
):
    review_valid = bool(
        baseline_ok
        and integrity_ok
        and audit_ok
        and response_locked
        and human_review_required
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if review_valid else 0

    state = (
        "FINAL_REVIEW_READY"
        if review_valid
        else "FINAL_REVIEW_BLOCKED"
    )

    return DefensiveFinalReview(
        baseline_ok=bool(baseline_ok),
        integrity_ok=bool(integrity_ok),
        audit_ok=bool(audit_ok),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        review_valid=review_valid,
        score=score,
        state=state,
    )


def final_review_to_dict(record):
    return {
        "baseline_ok": record.baseline_ok,
        "integrity_ok": record.integrity_ok,
        "audit_ok": record.audit_ok,
        "response_locked": record.response_locked,
        "human_review_required": record.human_review_required,
        "review_valid": record.review_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_final_review(record):
    if not isinstance(record, DefensiveFinalReview):
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
