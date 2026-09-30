"""Phase 68 — Defensive Recovery Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class RecoveryContinuity:
    recovery_plan_valid: bool
    rollback_valid: bool
    verification_valid: bool
    recovery_documented: bool
    continuity_valid: bool
    human_review_required: bool
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


def build_recovery_continuity(
    recovery_plan_valid=True,
    rollback_valid=True,
    verification_valid=True,
    recovery_documented=True,
):
    continuity_valid = all(
        [
            recovery_plan_valid,
            rollback_valid,
            verification_valid,
            recovery_documented,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = RecoveryContinuity(
        recovery_plan_valid=recovery_plan_valid,
        rollback_valid=rollback_valid,
        verification_valid=verification_valid,
        recovery_documented=recovery_documented,
        continuity_valid=continuity_valid,
        human_review_required=True,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return RecoveryContinuity(**data)


def recovery_continuity_to_dict(record):
    return asdict(record)


def validate_recovery_continuity(record):
    if not isinstance(record, RecoveryContinuity):
        return False

    data = asdict(record)

    if record.human_review_required is not True:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
