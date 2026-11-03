"""Phase 58 — Defensive Operational Readiness."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class OperationalReadiness:
    evidence_ready: bool
    alerts_ready: bool
    recovery_ready: bool
    audit_ready: bool
    controls_ready: bool
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


def build_operational_readiness(
    evidence_ready,
    alerts_ready,
    recovery_ready,
    audit_ready,
    controls_ready,
):
    checks = [
        evidence_ready,
        alerts_ready,
        recovery_ready,
        audit_ready,
        controls_ready,
    ]

    readiness_score = int((sum(checks) / 5) * 100)

    readiness_state = (
        "OPERATIONAL_DEFENSIVE_READY"
        if all(checks)
        else "OPERATIONAL_DEFENSIVE_HOLD"
    )

    payload = OperationalReadiness(
        evidence_ready=evidence_ready,
        alerts_ready=alerts_ready,
        recovery_ready=recovery_ready,
        audit_ready=audit_ready,
        controls_ready=controls_ready,
        readiness_score=readiness_score,
        readiness_state=readiness_state,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return OperationalReadiness(**data)


def readiness_to_dict(readiness):
    return asdict(readiness)


def validate_operational_readiness(readiness):
    if not isinstance(readiness, OperationalReadiness):
        return False

    data = asdict(readiness)

    if readiness.execution_blocked is not True:
        return False

    if not 0 <= readiness.readiness_score <= 100:
        return False

    if readiness.readiness_state not in {
        "OPERATIONAL_DEFENSIVE_READY",
        "OPERATIONAL_DEFENSIVE_HOLD",
    }:
        return False

    return readiness.digest == _digest(data)
