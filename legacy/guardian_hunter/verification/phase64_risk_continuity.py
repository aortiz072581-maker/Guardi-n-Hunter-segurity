"""Phase 64 — Defensive Risk Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class RiskContinuity:
    risk_score: int
    risk_valid: bool
    decision_valid: bool
    escalation_tracked: bool
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


def build_risk_continuity(
    risk_score=0,
    risk_valid=True,
    decision_valid=True,
    escalation_tracked=True,
):
    risk_score = max(0, min(100, int(risk_score)))

    continuity_valid = all(
        [
            risk_valid,
            decision_valid,
            escalation_tracked,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = RiskContinuity(
        risk_score=risk_score,
        risk_valid=risk_valid,
        decision_valid=decision_valid,
        escalation_tracked=escalation_tracked,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return RiskContinuity(**data)


def risk_to_dict(record):
    return asdict(record)


def validate_risk_continuity(record):
    if not isinstance(record, RiskContinuity):
        return False

    data = asdict(record)

    if not 0 <= record.risk_score <= 100:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
