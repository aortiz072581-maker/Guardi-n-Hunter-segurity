"""Phase 62 — Defensive System Readiness."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class SystemReadiness:
    evidence_ready: bool
    alerts_ready: bool
    incidents_ready: bool
    response_ready: bool
    governance_ready: bool
    continuity_ready: bool
    readiness_score: int
    readiness_state: str
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


def build_system_readiness(
    evidence_ready,
    alerts_ready,
    incidents_ready,
    response_ready,
    governance_ready,
    continuity_ready,
):
    checks = [
        evidence_ready,
        alerts_ready,
        incidents_ready,
        response_ready,
        governance_ready,
        continuity_ready,
    ]

    readiness_score = int((sum(checks) / 6) * 100)

    readiness_state = (
        "SYSTEM_DEFENSIVE_READY"
        if all(checks)
        else "SYSTEM_DEFENSIVE_HOLD"
    )

    payload = SystemReadiness(
        evidence_ready=evidence_ready,
        alerts_ready=alerts_ready,
        incidents_ready=incidents_ready,
        response_ready=response_ready,
        governance_ready=governance_ready,
        continuity_ready=continuity_ready,
        readiness_score=readiness_score,
        readiness_state=readiness_state,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return SystemReadiness(**data)


def readiness_to_dict(readiness):
    return asdict(readiness)


def validate_system_readiness(readiness):
    if not isinstance(readiness, SystemReadiness):
        return False

    data = asdict(readiness)

    if readiness.execution_blocked is not True:
        return False

    if not 0 <= readiness.readiness_score <= 100:
        return False

    if readiness.readiness_state not in {
        "SYSTEM_DEFENSIVE_READY",
        "SYSTEM_DEFENSIVE_HOLD",
    }:
        return False

    return readiness.digest == _digest(data)
