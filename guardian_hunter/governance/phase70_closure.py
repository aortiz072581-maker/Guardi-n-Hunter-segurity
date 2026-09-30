"""Phase 70 — Defensive Operational Closure."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class OperationalClosure:
    traceability_ready: bool
    recovery_ready: bool
    assurance_ready: bool
    governance_ready: bool
    closure_score: int
    closure_state: str
    response_locked: bool
    execution_blocked: bool
    final_review_required: bool
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


def build_operational_closure(
    traceability_ready,
    recovery_ready,
    assurance_ready,
    governance_ready,
):
    checks = [
        traceability_ready,
        recovery_ready,
        assurance_ready,
        governance_ready,
    ]

    closure_score = int((sum(checks) / 4) * 100)

    closure_state = (
        "DEFENSIVE_OPERATIONAL_CLOSED"
        if all(checks)
        else "DEFENSIVE_OPERATIONAL_HOLD"
    )

    payload = OperationalClosure(
        traceability_ready=traceability_ready,
        recovery_ready=recovery_ready,
        assurance_ready=assurance_ready,
        governance_ready=governance_ready,
        closure_score=closure_score,
        closure_state=closure_state,
        response_locked=True,
        execution_blocked=not EXECUTION_ALLOWED,
        final_review_required=True,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return OperationalClosure(**data)


def closure_to_dict(record):
    return asdict(record)


def validate_operational_closure(record):
    if not isinstance(record, OperationalClosure):
        return False

    data = asdict(record)

    if record.response_locked is not True:
        return False

    if record.execution_blocked is not True:
        return False

    if record.final_review_required is not True:
        return False

    if not 0 <= record.closure_score <= 100:
        return False

    if record.closure_state not in {
        "DEFENSIVE_OPERATIONAL_CLOSED",
        "DEFENSIVE_OPERATIONAL_HOLD",
    }:
        return False

    return record.digest == _digest(data)
