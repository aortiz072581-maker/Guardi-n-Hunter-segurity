"""Phase 69 — Defensive Assurance Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveAssurance:
    traceability_valid: bool
    evidence_valid: bool
    recovery_valid: bool
    governance_valid: bool
    assurance_score: int
    assurance_state: str
    response_locked: bool
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


def build_assurance(
    traceability_valid,
    evidence_valid,
    recovery_valid,
    governance_valid,
):
    checks = [
        traceability_valid,
        evidence_valid,
        recovery_valid,
        governance_valid,
    ]

    assurance_score = int((sum(checks) / 4) * 100)

    assurance_state = (
        "DEFENSIVE_ASSURANCE_READY"
        if all(checks)
        else "DEFENSIVE_ASSURANCE_HOLD"
    )

    payload = DefensiveAssurance(
        traceability_valid=traceability_valid,
        evidence_valid=evidence_valid,
        recovery_valid=recovery_valid,
        governance_valid=governance_valid,
        assurance_score=assurance_score,
        assurance_state=assurance_state,
        response_locked=True,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DefensiveAssurance(**data)


def assurance_to_dict(record):
    return asdict(record)


def validate_assurance(record):
    if not isinstance(record, DefensiveAssurance):
        return False

    data = asdict(record)

    if record.response_locked is not True:
        return False

    if record.execution_blocked is not True:
        return False

    if not 0 <= record.assurance_score <= 100:
        return False

    if record.assurance_state not in {
        "DEFENSIVE_ASSURANCE_READY",
        "DEFENSIVE_ASSURANCE_HOLD",
    }:
        return False

    return record.digest == _digest(data)
