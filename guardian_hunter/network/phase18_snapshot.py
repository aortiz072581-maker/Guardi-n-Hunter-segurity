"""Guardian Hunter — Phase 18.4
Network Security Snapshot
READ_ONLY / DRY_RUN only.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class NetworkSecuritySnapshot:
    baseline_integrity: bool
    total_changes: int
    anomaly_count: int
    anomaly_score: float
    risk_level: str
    interfaces_status: str
    gateway_status: str
    dns_status: str
    listeners_status: str
    egress_status: str
    phase: int = 18
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _risk_level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def build_network_security_snapshot(
    baseline_valid: bool,
    diff,
    anomalies: List[Any],
    anomaly_score: float,
    current: Dict[str, Any],
) -> NetworkSecuritySnapshot:

    def status(field: str) -> str:
        return "CHANGED" if (
            field in diff.changed and diff.changed[field]
        ) else "OK"

    return NetworkSecuritySnapshot(
        baseline_integrity=bool(baseline_valid),
        total_changes=diff.total_changes,
        anomaly_count=len(anomalies),
        anomaly_score=float(anomaly_score),
        risk_level=_risk_level(float(anomaly_score)),
        interfaces_status=status("interfaces"),
        gateway_status=status("gateways"),
        dns_status=status("dns_servers"),
        listeners_status=status("listeners"),
        egress_status=status("egress_destinations"),
    )


def snapshot_to_dict(
    snapshot: NetworkSecuritySnapshot,
) -> Dict[str, Any]:
    return asdict(snapshot)


def validate_network_snapshot(
    snapshot: NetworkSecuritySnapshot,
) -> bool:
    return (
        snapshot.phase == 18
        and snapshot.mode == "READ_ONLY"
        and snapshot.execution_allowed is False
        and 0.0 <= snapshot.anomaly_score <= 100.0
        and snapshot.risk_level in {
            "NORMAL",
            "WATCH",
            "HIGH",
            "CRITICAL",
        }
    )


__all__ = [
    "NetworkSecuritySnapshot",
    "build_network_security_snapshot",
    "snapshot_to_dict",
    "validate_network_snapshot",
]
