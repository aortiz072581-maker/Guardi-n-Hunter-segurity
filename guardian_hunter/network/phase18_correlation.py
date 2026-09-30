"""Phase 18.9 — Advanced Hardware ↔ Network Correlation."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class HardwareNetworkCorrelation:
    matched: List[Dict[str, Any]]
    unmatched_hardware: List[Dict[str, Any]]
    unmatched_network: List[Dict[str, Any]]
    correlation_count: int
    confidence: float
    phase: str = "18.9"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _items(value: Any) -> List[Dict[str, Any]]:
    if value is None:
        return []

    if isinstance(value, dict):
        return [dict(value)]

    if isinstance(value, (list, tuple)):
        return [
            dict(item)
            for item in value
            if isinstance(item, dict)
        ]

    return []


def _key(item: Dict[str, Any]) -> str:
    for field in (
        "mac",
        "mac_address",
        "hardware_address",
        "interface",
        "interface_name",
        "name",
        "id",
    ):
        value = _norm(item.get(field))
        if value:
            return value

    return ""


def correlate_hardware_network(
    hardware: Any,
    network: Any,
) -> HardwareNetworkCorrelation:

    hardware_items = _items(hardware)
    network_items = _items(network)

    network_by_key = {}

    for item in network_items:
        key = _key(item)

        if key:
            network_by_key.setdefault(key, []).append(item)

    matched = []
    unmatched_hardware = []

    for hw in hardware_items:
        key = _key(hw)

        if key and key in network_by_key:
            matched.append(
                {
                    "hardware": dict(hw),
                    "network": [
                        dict(item)
                        for item in network_by_key[key]
                    ],
                    "correlation_key": key,
                }
            )
        else:
            unmatched_hardware.append(dict(hw))

    matched_keys = {
        item["correlation_key"]
        for item in matched
    }

    unmatched_network = []

    for item in network_items:
        key = _key(item)

        if not key or key not in matched_keys:
            unmatched_network.append(dict(item))

    total = len(hardware_items) + len(network_items)

    confidence = (
        round(
            (len(matched) / max(len(hardware_items), 1)) * 100,
            2,
        )
        if total
        else 0.0
    )

    return HardwareNetworkCorrelation(
        matched=matched,
        unmatched_hardware=unmatched_hardware,
        unmatched_network=unmatched_network,
        correlation_count=len(matched),
        confidence=min(confidence, 100.0),
    )


def correlation_to_dict(
    correlation: HardwareNetworkCorrelation,
) -> Dict[str, Any]:
    return asdict(correlation)


def validate_hardware_network_correlation(
    correlation: HardwareNetworkCorrelation,
) -> bool:

    return (
        isinstance(correlation, HardwareNetworkCorrelation)
        and isinstance(correlation.matched, list)
        and isinstance(correlation.unmatched_hardware, list)
        and isinstance(correlation.unmatched_network, list)
        and isinstance(correlation.correlation_count, int)
        and 0 <= correlation.confidence <= 100
        and correlation.phase == "18.9"
        and correlation.mode == "READ_ONLY"
        and correlation.execution_allowed is False
    )
