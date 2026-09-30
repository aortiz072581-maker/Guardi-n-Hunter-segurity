"""Guardian Hunter — Phase 18.3
Network Anomaly Detection
READ_ONLY / DRY_RUN only.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class NetworkAnomaly:
    anomaly_type: str
    field: str
    severity: str
    description: str
    evidence_count: int
    phase: int = 18
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _severity(field: str, change_type: str) -> str:
    high = {
        "gateways",
        "dns_servers",
        "listeners",
        "mac_addresses",
    }

    medium = {
        "routes",
        "connections",
        "egress_destinations",
    }

    if field in high:
        return "HIGH"

    if field in medium:
        return "MEDIUM"

    return "LOW"


def detect_network_anomalies(diff) -> List[NetworkAnomaly]:
    anomalies: List[NetworkAnomaly] = []

    for field, values in diff.added.items():
        if values:
            severity = _severity(field, "added")

            anomalies.append(
                NetworkAnomaly(
                    anomaly_type="NEW_NETWORK_STATE",
                    field=field,
                    severity=severity,
                    description=f"New network state detected in {field}",
                    evidence_count=len(values),
                )
            )

    for field, values in diff.removed.items():
        if values:
            severity = _severity(field, "removed")

            anomalies.append(
                NetworkAnomaly(
                    anomaly_type="REMOVED_NETWORK_STATE",
                    field=field,
                    severity=severity,
                    description=f"Network state removed from {field}",
                    evidence_count=len(values),
                )
            )

    return anomalies


def calculate_network_anomaly_score(
    anomalies: List[NetworkAnomaly],
) -> float:
    weights = {
        "LOW": 10.0,
        "MEDIUM": 20.0,
        "HIGH": 30.0,
    }

    score = sum(
        weights.get(item.severity, 0.0)
        for item in anomalies
    )

    return min(100.0, score)


def validate_network_anomalies(
    anomalies: List[NetworkAnomaly],
) -> bool:
    return all(
        item.phase == 18
        and item.mode == "READ_ONLY"
        and item.execution_allowed is False
        and item.severity in {"LOW", "MEDIUM", "HIGH"}
        for item in anomalies
    )


def anomaly_records(
    anomalies: List[NetworkAnomaly],
) -> List[Dict]:
    return [asdict(item) for item in anomalies]


__all__ = [
    "NetworkAnomaly",
    "detect_network_anomalies",
    "calculate_network_anomaly_score",
    "validate_network_anomalies",
    "anomaly_records",
]
