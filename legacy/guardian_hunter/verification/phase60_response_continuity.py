"""Phase 60 — Defensive Response Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class ResponseContinuity:
    response_plan_valid: bool
    response_locked: bool
    rollback_ready: bool
    human_review_required: bool
    continuity_valid: bool
    execution_blocked: bool
    digest: str = ""


def _canonical(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _digest(data):
    clean = dict(data)
    clean.pop("digest", None)
    return sha256(_canonical(clean).encode()).hexdigest()


def build_response_continuity(
    response_plan_valid=True,
    response_locked=True,
    rollback_ready=True,
):
    continuity_valid = all(
        [
            response_plan_valid,
            response_locked,
            rollback_ready,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = ResponseContinuity(
        response_plan_valid=response_plan_valid,
        response_locked=response_locked,
        rollback_ready=rollback_ready,
        human_review_required=True,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return ResponseContinuity(**data)


def response_to_dict(record):
    return asdict(record)


def validate_response_continuity(record):
    if not isinstance(record, ResponseContinuity):
        return False

    data = asdict(record)

    if record.response_locked is not True:
        return False

    if record.human_review_required is not True:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
