"""Phase 18.12 — Network Defense Integration."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkDefenseIntegration:
    baseline: Dict[str, Any]
    diff: Dict[str, Any]
    anomalies: Dict[str, Any]
    dns: Dict[str, Any]
    listeners: Dict[str, Any]
    connections: Dict[str, Any]
    timeline: Dict[str, Any]
    correlation: Dict[str, Any]
    risk: Dict[str, Any]
    evidence: Dict[str, Any]
    integrity_digest: str
    integration_status: str
    phase: str = "18.12"
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


def _mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)

    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)

    return {}


def build_network_defense_integration(
    baseline: Any,
    diff: Any,
    anomalies: Any,
    dns: Any,
    listeners: Any,
    connections: Any,
    timeline: Any,
    correlation: Any,
    risk: Any,
    evidence: Any,
) -> NetworkDefenseIntegration:

    payload = {
        "baseline": _mapping(baseline),
        "diff": _mapping(diff),
        "anomalies": _mapping(anomalies),
        "dns": _mapping(dns),
        "listeners": _mapping(listeners),
        "connections": _mapping(connections),
        "timeline": _mapping(timeline),
        "correlation": _mapping(correlation),
        "risk": _mapping(risk),
        "evidence": _mapping(evidence),
    }

    digest = _digest(payload)

    return NetworkDefenseIntegration(
        **payload,
        integrity_digest=digest,
        integration_status="INTEGRATED_READ_ONLY",
    )


def integration_to_dict(
    integration: NetworkDefenseIntegration,
) -> Dict[str, Any]:
    return asdict(integration)


def validate_network_defense_integration(
    integration: NetworkDefenseIntegration,
) -> bool:

    if not isinstance(
        integration,
        NetworkDefenseIntegration,
    ):
        return False

    if integration.phase != "18.12":
        return False

    if integration.mode != "READ_ONLY":
        return False

    if integration.execution_allowed is not False:
        return False

    payload = {
        "baseline": integration.baseline,
        "diff": integration.diff,
        "anomalies": integration.anomalies,
        "dns": integration.dns,
        "listeners": integration.listeners,
        "connections": integration.connections,
        "timeline": integration.timeline,
        "correlation": integration.correlation,
        "risk": integration.risk,
        "evidence": integration.evidence,
    }

    return (
        integration.integration_status
        == "INTEGRATED_READ_ONLY"
        and integration.integrity_digest
        == _digest(payload)
    )
