"""Guardian Hunter - passive network defense signals."""

from __future__ import annotations

import re
import socket
import subprocess
from typing import Any


def _run(command: list[str]) -> str:
    if not isinstance(command, list) or tuple(command) not in {("ip", "route"), ("ip", "neigh"), ("ip", "-brief", "addr")} :
        return ""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def collect_network_signals() -> dict[str, Any]:
    """Collect passive network signals."""
    routes = _run(["ip", "route"])
    neighbors = _run(["ip", "neigh"])
    interfaces = _run(["ip", "-brief", "addr"])

    gateways = []

    for line in routes.splitlines():
        parts = line.split()
        if "default" in parts:
            try:
                index = parts.index("via")
                gateways.append(parts[index + 1])
            except (ValueError, IndexError):
                import logging; logging.getLogger(__name__).warning('fail-closed %s:%d %s', __file__, 41, _e)

    neighbor_entries = []

    for line in neighbors.splitlines():
        parts = line.split()

        if not parts:
            continue

        entry = {
            "raw": line,
            "ip": parts[0],
            "mac": None,
            "state": parts[-1] if len(parts) > 1 else None,
        }

        if "lladdr" in parts:
            try:
                entry["mac"] = parts[parts.index("lladdr") + 1]
            except (ValueError, IndexError):
                import logging; logging.getLogger(__name__).warning('fail-closed %s:%d %s', __file__, 62, _e)

        neighbor_entries.append(entry)

    return {
        "interfaces": interfaces,
        "routes": routes,
        "gateways": sorted(set(gateways)),
        "neighbors": neighbor_entries,
    }


def compare_network_baseline(
    previous: dict,
    current: dict,
) -> dict:
    """Compare passive network snapshots."""
    old_gateways = set(previous.get("gateways", []))
    new_gateways = set(current.get("gateways", []))

    old_neighbors = {
        (item.get("ip"), item.get("mac"))
        for item in previous.get("neighbors", [])
        if isinstance(item, dict)
    }

    new_neighbors = {
        (item.get("ip"), item.get("mac"))
        for item in current.get("neighbors", [])
        if isinstance(item, dict)
    }

    return {
        "new_gateways": sorted(new_gateways - old_gateways),
        "removed_gateways": sorted(old_gateways - new_gateways),
        "new_neighbors": sorted(new_neighbors - old_neighbors),
        "removed_neighbors": sorted(old_neighbors - new_neighbors),
        "gateway_changed": old_gateways != new_gateways,
        "neighbor_changed": old_neighbors != new_neighbors,
    }


def resolve_destination(host: str) -> dict:
    """Resolve a destination without connecting to it."""
    try:
        addresses = sorted(
            {
                item[4][0]
                for item in socket.getaddrinfo(
                    host,
                    None,
                    family=socket.AF_UNSPEC,
                )
            }
        )
    except (socket.gaierror, OSError):
        addresses = []

    return {
        "host": host,
        "addresses": addresses,
        "resolved": bool(addresses),
    }