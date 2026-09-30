"""Guardian Hunter — Phase 18.1
Network Baseline 2.0
READ_ONLY / DRY_RUN only.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class NetworkBaseline:
    interfaces: tuple
    addresses: tuple
    mac_addresses: tuple
    gateways: tuple
    routes: tuple
    dns_servers: tuple
    listeners: tuple
    connections: tuple
    egress_destinations: tuple
    digest: str
    phase: int = 18
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _normalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple, set)):
        return sorted(
            (_normalize(v) for v in value),
            key=lambda x: json.dumps(x, sort_keys=True, default=str),
        )
    return value


def _digest(data: Dict[str, Any]) -> str:
    canonical = json.dumps(
        _normalize(data),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def create_network_baseline(snapshot: Dict[str, Any]) -> NetworkBaseline:
    data = {
        "interfaces": snapshot.get("interfaces", []),
        "addresses": snapshot.get("addresses", snapshot.get("ips", [])),
        "mac_addresses": snapshot.get("mac_addresses", snapshot.get("macs", [])),
        "gateways": snapshot.get("gateways", []),
        "routes": snapshot.get("routes", []),
        "dns_servers": snapshot.get("dns_servers", snapshot.get("dns", [])),
        "listeners": snapshot.get("listeners", []),
        "connections": snapshot.get("connections", []),
        "egress_destinations": snapshot.get(
            "egress_destinations",
            snapshot.get("egress", []),
        ),
    }

    return NetworkBaseline(
        interfaces=tuple(_normalize(data["interfaces"])),
        addresses=tuple(_normalize(data["addresses"])),
        mac_addresses=tuple(_normalize(data["mac_addresses"])),
        gateways=tuple(_normalize(data["gateways"])),
        routes=tuple(_normalize(data["routes"])),
        dns_servers=tuple(_normalize(data["dns_servers"])),
        listeners=tuple(_normalize(data["listeners"])),
        connections=tuple(_normalize(data["connections"])),
        egress_destinations=tuple(_normalize(data["egress_destinations"])),
        digest=_digest(data),
    )


def baseline_to_dict(baseline: NetworkBaseline) -> Dict[str, Any]:
    result = asdict(baseline)
    for key in (
        "interfaces",
        "addresses",
        "mac_addresses",
        "gateways",
        "routes",
        "dns_servers",
        "listeners",
        "connections",
        "egress_destinations",
    ):
        result[key] = list(result[key])
    return result


def validate_network_baseline(baseline: NetworkBaseline) -> bool:
    return (
        baseline.phase == 18
        and baseline.mode == "READ_ONLY"
        and baseline.execution_allowed is False
        and bool(baseline.digest)
        and len(baseline.digest) == 64
    )


__all__ = [
    "NetworkBaseline",
    "create_network_baseline",
    "baseline_to_dict",
    "validate_network_baseline",
    "READ_ONLY",
    "DRY_RUN",
    "EXECUTION_ALLOWED",
]
