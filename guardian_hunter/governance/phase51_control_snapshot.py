"""Phase 51 — Defensive Control Snapshot."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveControlSnapshot:
    read_only: bool
    dry_run: bool
    execution_allowed: bool
    audit_trail: bool
    evidence_integrity: bool
    baseline_integrity: bool
    response_locked: bool
    health_gate: bool
    controls_valid: bool
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


def build_control_snapshot(
    audit_trail=True,
    evidence_integrity=True,
    baseline_integrity=True,
    response_locked=True,
    health_gate=True,
):
    controls_valid = all(
        [
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
            audit_trail,
            evidence_integrity,
            baseline_integrity,
            response_locked,
            health_gate,
        ]
    )

    payload = DefensiveControlSnapshot(
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
        audit_trail=audit_trail,
        evidence_integrity=evidence_integrity,
        baseline_integrity=baseline_integrity,
        response_locked=response_locked,
        health_gate=health_gate,
        controls_valid=controls_valid,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DefensiveControlSnapshot(**data)


def snapshot_to_dict(snapshot):
    return asdict(snapshot)


def validate_control_snapshot(snapshot):
    if not isinstance(snapshot, DefensiveControlSnapshot):
        return False

    data = asdict(snapshot)

    if data["read_only"] is not True:
        return False

    if data["dry_run"] is not True:
        return False

    if data["execution_allowed"] is not False:
        return False

    if data["controls_valid"] is not True:
        return False

    return data["digest"] == _digest(data)
