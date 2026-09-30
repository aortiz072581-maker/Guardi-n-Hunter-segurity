"""Phase 18.14 — Network Case/Evidence Bridge."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkCaseBridge:
    case_reference: str
    evidence_reference: str
    risk_level: str
    risk_score: float
    bridge_status: str
    digest: str
    phase: str = "18.14"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _canonical(payload: Dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _digest(payload: Dict[str, Any]) -> str:
    return sha256(
        _canonical(payload).encode("utf-8")
    ).hexdigest()


def build_network_case_bridge(
    case_reference: Any,
    evidence_reference: Any,
    risk_score: Any,
    risk_level: Any,
) -> NetworkCaseBridge:

    try:
        score = max(
            0.0,
            min(float(risk_score), 100.0),
        )
    except (TypeError, ValueError):
        score = 0.0

    payload = {
        "case_reference": str(case_reference),
        "evidence_reference": str(evidence_reference),
        "risk_level": str(risk_level),
        "risk_score": score,
        "phase": "18.14",
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    digest = _digest(payload)

    return NetworkCaseBridge(
        case_reference=str(case_reference),
        evidence_reference=str(evidence_reference),
        risk_level=str(risk_level),
        risk_score=score,
        bridge_status="LINKED_READ_ONLY",
        digest=digest,
    )


def bridge_to_dict(
    bridge: NetworkCaseBridge,
) -> Dict[str, Any]:
    return asdict(bridge)


def validate_network_case_bridge(
    bridge: NetworkCaseBridge,
) -> bool:

    if not isinstance(bridge, NetworkCaseBridge):
        return False

    payload = {
        "case_reference": bridge.case_reference,
        "evidence_reference": bridge.evidence_reference,
        "risk_level": bridge.risk_level,
        "risk_score": bridge.risk_score,
        "phase": "18.14",
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    return (
        bridge.phase == "18.14"
        and bridge.mode == "READ_ONLY"
        and bridge.execution_allowed is False
        and bridge.bridge_status
        == "LINKED_READ_ONLY"
        and bridge.digest == _digest(payload)
    )
