"""Phase 59 — Defensive Incident Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class IncidentContinuity:
    incident_count: int
    incidents_valid: bool
    evidence_linked: bool
    audit_linked: bool
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


def build_incident_continuity(
    incident_count=0,
    incidents_valid=True,
    evidence_linked=True,
    audit_linked=True,
):
    incident_count = max(0, int(incident_count))

    continuity_valid = all(
        [
            incidents_valid,
            evidence_linked,
            audit_linked,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = IncidentContinuity(
        incident_count=incident_count,
        incidents_valid=incidents_valid,
        evidence_linked=evidence_linked,
        audit_linked=audit_linked,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return IncidentContinuity(**data)


def incident_to_dict(record):
    return asdict(record)


def validate_incident_continuity(record):
    if not isinstance(record, IncidentContinuity):
        return False

    data = asdict(record)

    if record.incident_count < 0:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
