"""Phase 65 — Defensive Decision Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DecisionContinuity:
    decision_valid: bool
    policy_valid: bool
    human_review_required: bool
    response_locked: bool
    decision_state: str
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


def build_decision_continuity(
    decision_valid=True,
    policy_valid=True,
    human_review_required=False,
    response_locked=True,
):
    continuity_valid = all(
        [
            decision_valid,
            policy_valid,
            response_locked,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    decision_state = (
        "DEFENSIVE_DECISION_READY"
        if continuity_valid
        else "DEFENSIVE_DECISION_HOLD"
    )

    payload = DecisionContinuity(
        decision_valid=decision_valid,
        policy_valid=policy_valid,
        human_review_required=human_review_required,
        response_locked=response_locked,
        decision_state=decision_state,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DecisionContinuity(**data)


def decision_to_dict(record):
    return asdict(record)


def validate_decision_continuity(record):
    if not isinstance(record, DecisionContinuity):
        return False

    data = asdict(record)

    if record.response_locked is not True:
        return False

    if record.execution_blocked is not True:
        return False

    if record.decision_state not in {
        "DEFENSIVE_DECISION_READY",
        "DEFENSIVE_DECISION_HOLD",
    }:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
