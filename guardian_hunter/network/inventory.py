"""Guardian Hunter - passive network inventory."""

from __future__ import annotations

import socket
import subprocess


def _run(command: list[str]) -> str:
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


def collect_network_inventory() -> dict:
    """Collect network state without changing it."""
    hostname = socket.gethostname()

    addresses = []
    try:
        for item in socket.getaddrinfo(
            hostname,
            None,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        ):
            address = item[4][0]
            if address not in addresses:
                addresses.append(address)
    except socket.gaierror:
        pass

    return {
        "hostname": hostname,
        "addresses": sorted(addresses),
        "interfaces": _run(["ip", "-brief", "addr"]),
        "routes": _run(["ip", "route"]),
        "neighbors": _run(["ip", "neigh"]),
    }


def detect_network_changes(previous: dict, current: dict) -> dict:
    """Detect changes between two snapshots."""
    return {
        "addresses_changed": (
            previous.get("addresses", []) != current.get("addresses", [])
        ),
        "interfaces_changed": (
            previous.get("interfaces", "") != current.get("interfaces", "")
        ),
        "routes_changed": (
            previous.get("routes", "") != current.get("routes", "")
        ),
        "neighbors_changed": (
            previous.get("neighbors", "") != current.get("neighbors", "")
        ),
    }
