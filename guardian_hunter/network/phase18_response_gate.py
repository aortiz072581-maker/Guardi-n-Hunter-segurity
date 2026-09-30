"""Phase 18.15 — Defensive Response Gate."""

from dataclasses import dataclass, asdict
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkResponseGate:
    risk_level: str
    evidence_valid: bool
    integrity_valid: bool
    response_locked: bool
    allowed_response: str
    gate_status: str
    phase: str = "18.15"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def build_network_response_gate(
    risk_level: Any,
    evidence_valid: Any = True,
    integrity_valid: Any = True,
) -> NetworkResponseGate:

    level = str(risk_level).upper()
    evidence_ok = bool(evidence_valid)
    integrity_ok = bool(integrity_valid)

    # Defensive response is descriptive only.
    # No actual containment, firewall, process termination,
    # routing change, or network modification is performed.

    if not evidence_ok or not integrity_ok:
        response = "HOLD_AND_VALIDATE"
        status = "BLOCKED_BY_INTEGRITY"
    elif level == "CRITICAL":
        response = "ESCALATE_FOR_REVIEW"
        status = "READY_FOR_REVIEW"
    elif level == "HIGH":
        response = "ENHANCED_MONITORING"
        status = "READY_FOR_REVIEW"
    elif level == "WATCH":
        response = "MONITOR"
        status = "READY_FOR_REVIEW"
    else:
        response = "CONTINUE_MONITORING"
        status = "READY"

    return NetworkResponseGate(
        risk_level=level,
        evidence_valid=evidence_ok,
        integrity_valid=integrity_ok,
        response_locked=True,
        allowed_response=response,
        gate_status=status,
    )


def response_gate_to_dict(
    gate: NetworkResponseGate,
) -> Dict[str, Any]:
    return asdict(gate)


def validate_network_response_gate(
    gate: NetworkResponseGate,
) -> bool:

    return (
        isinstance(gate, NetworkResponseGate)
        and gate.response_locked is True
        and gate.gate_status in {
            "READY",
            "READY_FOR_REVIEW",
            "BLOCKED_BY_INTEGRITY",
        }
        and gate.phase == "18.15"
        and gate.mode == "READ_ONLY"
        and gate.execution_allowed is False
    )
