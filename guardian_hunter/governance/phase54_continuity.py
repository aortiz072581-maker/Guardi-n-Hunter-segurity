"""Phase 54 — Defensive Release Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveContinuity:
    controls_valid: bool
    integrity_valid: bool
    state_gate_valid: bool
    audit_valid: bool
    continuity_score: int
    release_state: str
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


def build_continuity(
    controls_valid,
    integrity_valid,
    state_gate_valid,
    audit_valid,
):
    checks = [
        controls_valid,
        integrity_valid,
        state_gate_valid,
        audit_valid,
    ]

    continuity_score = int((sum(checks) / 4) * 100)

    release_state = (
        "CONTINUITY_READY"
        if all(checks)
        else "CONTINUITY_HOLD"
    )

    payload = DefensiveContinuity(
        controls_valid=controls_valid,
        integrity_valid=integrity_valid,
        state_gate_valid=state_gate_valid,
        audit_valid=audit_valid,
        continuity_score=continuity_score,
        release_state=release_state,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DefensiveContinuity(**data)


def continuity_to_dict(continuity):
    return asdict(continuity)


def validate_continuity(continuity):
    if not isinstance(continuity, DefensiveContinuity):
        return False

    data = asdict(continuity)

    if continuity.execution_blocked is not True:
        return False

    if continuity.continuity_score < 0:
        return False

    if continuity.continuity_score > 100:
        return False

    if continuity.release_state not in {
        "CONTINUITY_READY",
        "CONTINUITY_HOLD",
    }:
        return False

    return continuity.digest == _digest(data)
