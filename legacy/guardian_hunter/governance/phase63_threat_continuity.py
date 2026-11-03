"""Phase 63 — Defensive Threat Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class ThreatContinuity:
    signal_count: int
    threat_analysis_valid: bool
    correlation_valid: bool
    risk_valid: bool
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


def build_threat_continuity(
    signal_count=0,
    threat_analysis_valid=True,
    correlation_valid=True,
    risk_valid=True,
):
    signal_count = max(0, int(signal_count))

    continuity_valid = all(
        [
            threat_analysis_valid,
            correlation_valid,
            risk_valid,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = ThreatContinuity(
        signal_count=signal_count,
        threat_analysis_valid=threat_analysis_valid,
        correlation_valid=correlation_valid,
        risk_valid=risk_valid,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return ThreatContinuity(**data)


def threat_to_dict(record):
    return asdict(record)


def validate_threat_continuity(record):
    if not isinstance(record, ThreatContinuity):
        return False

    data = asdict(record)

    if record.signal_count < 0:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
