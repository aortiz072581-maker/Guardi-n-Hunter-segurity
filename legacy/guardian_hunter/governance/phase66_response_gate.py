"""Phase 66 — Defensive Threat-to-Response Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class ThreatResponseGate:
    threat_ready: bool
    risk_ready: bool
    decision_ready: bool
    evidence_ready: bool
    response_locked: bool
    human_review_required: bool
    response_state: str
    gate_score: int
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


def build_threat_response_gate(
    threat_ready,
    risk_ready,
    decision_ready,
    evidence_ready,
):
    checks = [
        threat_ready,
        risk_ready,
        decision_ready,
        evidence_ready,
    ]

    gate_score = int((sum(checks) / 4) * 100)

    response_ready = all(checks)

    response_state = (
        "RESPONSE_READY_FOR_REVIEW"
        if response_ready
        else "RESPONSE_GATE_HOLD"
    )

    payload = ThreatResponseGate(
        threat_ready=threat_ready,
        risk_ready=risk_ready,
        decision_ready=decision_ready,
        evidence_ready=evidence_ready,
        response_locked=True,
        human_review_required=True,
        response_state=response_state,
        gate_score=gate_score,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return ThreatResponseGate(**data)


def response_gate_to_dict(gate):
    return asdict(gate)


def validate_threat_response_gate(gate):
    if not isinstance(gate, ThreatResponseGate):
        return False

    data = asdict(gate)

    if gate.response_locked is not True:
        return False

    if gate.human_review_required is not True:
        return False

    if gate.execution_blocked is not True:
        return False

    if not 0 <= gate.gate_score <= 100:
        return False

    if gate.response_state not in {
        "RESPONSE_READY_FOR_REVIEW",
        "RESPONSE_GATE_HOLD",
    }:
        return False

    return gate.digest == _digest(data)
