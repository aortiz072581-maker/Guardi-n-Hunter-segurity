"""Phase 38 — Defensive Operations Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class DefensiveOperationsGate:
    control_matrix_ok: bool
    integrity_ok: bool
    continuity_ok: bool
    audit_ok: bool
    evidence_ok: bool
    baseline_ok: bool
    response_locked: bool
    safety_score: int
    operations_ready: bool
    execution_blocked: bool
    digest: str
    mode: str
    status: str


def _canonical(data: Dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _digest(data: Dict[str, Any]) -> str:
    return sha256(
        _canonical(data).encode("utf-8")
    ).hexdigest()


def build_operations_gate(
    control_matrix_ok: bool,
    integrity_ok: bool,
    continuity_ok: bool,
    audit_ok: bool,
    evidence_ok: bool,
    baseline_ok: bool,
    response_locked: bool,
) -> DefensiveOperationsGate:

    controls = [
        bool(control_matrix_ok),
        bool(integrity_ok),
        bool(continuity_ok),
        bool(audit_ok),
        bool(evidence_ok),
        bool(baseline_ok),
        bool(response_locked),
    ]

    score = int(
        (sum(controls) / len(controls)) * 100
    )

    ready = all(controls)

    payload = {
        "control_matrix_ok": bool(control_matrix_ok),
        "integrity_ok": bool(integrity_ok),
        "continuity_ok": bool(continuity_ok),
        "audit_ok": bool(audit_ok),
        "evidence_ok": bool(evidence_ok),
        "baseline_ok": bool(baseline_ok),
        "response_locked": bool(response_locked),
        "safety_score": score,
        "operations_ready": ready,
        "execution_blocked": True,
        "mode": "READ_ONLY",
    }

    return DefensiveOperationsGate(
        control_matrix_ok=bool(control_matrix_ok),
        integrity_ok=bool(integrity_ok),
        continuity_ok=bool(continuity_ok),
        audit_ok=bool(audit_ok),
        evidence_ok=bool(evidence_ok),
        baseline_ok=bool(baseline_ok),
        response_locked=bool(response_locked),
        safety_score=score,
        operations_ready=ready,
        execution_blocked=True,
        digest=_digest(payload),
        mode="READ_ONLY",
        status=(
            "DEFENSIVE_OPERATIONS_READY"
            if ready
            else "DEFENSIVE_OPERATIONS_HOLD"
        ),
    )


def operations_to_dict(
    gate: DefensiveOperationsGate,
) -> Dict[str, Any]:
    return asdict(gate)


def validate_operations_gate(
    gate: DefensiveOperationsGate,
) -> bool:
    return (
        isinstance(gate, DefensiveOperationsGate)
        and 0 <= gate.safety_score <= 100
        and gate.operations_ready
        == (
            gate.control_matrix_ok
            and gate.integrity_ok
            and gate.continuity_ok
            and gate.audit_ok
            and gate.evidence_ok
            and gate.baseline_ok
            and gate.response_locked
        )
        and gate.execution_blocked is True
        and len(gate.digest) == 64
        and gate.mode == "READ_ONLY"
    )
