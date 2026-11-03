"""Phase 56 — Defensive Alert Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class AlertContinuity:
    alert_count: int
    alerts_valid: bool
    correlation_valid: bool
    alerts_preserved: bool
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


def build_alert_continuity(
    alert_count=0,
    alerts_valid=True,
    correlation_valid=True,
):
    alert_count = max(0, int(alert_count))

    alerts_preserved = (
        alerts_valid
        and correlation_valid
        and READ_ONLY
        and DRY_RUN
    )

    continuity_valid = alerts_preserved

    payload = AlertContinuity(
        alert_count=alert_count,
        alerts_valid=alerts_valid,
        correlation_valid=correlation_valid,
        alerts_preserved=alerts_preserved,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return AlertContinuity(**data)


def alert_continuity_to_dict(record):
    return asdict(record)


def validate_alert_continuity(record):
    if not isinstance(record, AlertContinuity):
        return False

    data = asdict(record)

    if record.alert_count < 0:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
