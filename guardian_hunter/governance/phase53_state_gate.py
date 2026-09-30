"""Phase 53 — Defensive State Transition Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveStateGate:
    current_state: str
    requested_state: str
    transition_allowed: bool
    requires_human_review: bool
    execution_blocked: bool
    reason: str
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


def build_state_gate(current_state, requested_state):
    safe_states = {
        "MONITORING",
        "ENHANCED_MONITORING",
        "ESCALATION_REVIEW",
        "RECOVERY_REVIEW",
    }

    valid_request = (
        current_state in safe_states
        and requested_state in safe_states
    )

    transition_allowed = (
        valid_request
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    requires_human_review = requested_state in {
        "ESCALATION_REVIEW",
        "RECOVERY_REVIEW",
    }

    reason = (
        "DEFENSIVE_STATE_TRANSITION_ALLOWED"
        if transition_allowed
        else "STATE_TRANSITION_BLOCKED"
    )

    payload = DefensiveStateGate(
        current_state=current_state,
        requested_state=requested_state,
        transition_allowed=transition_allowed,
        requires_human_review=requires_human_review,
        execution_blocked=not EXECUTION_ALLOWED,
        reason=reason,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DefensiveStateGate(**data)


def state_gate_to_dict(gate):
    return asdict(gate)


def validate_state_gate(gate):
    if not isinstance(gate, DefensiveStateGate):
        return False

    data = asdict(gate)

    if gate.execution_blocked is not True:
        return False

    if gate.transition_allowed is not True:
        return False

    if not gate.reason:
        return False

    return gate.digest == _digest(data)
