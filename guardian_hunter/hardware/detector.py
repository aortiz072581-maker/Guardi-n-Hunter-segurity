"""Guardian Hunter - hardware inventory.

Passive inventory only.
No device modification or blocking is performed here.
"""

from __future__ import annotations

import hashlib
import os
import platform
from pathlib import Path


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:16]


def _read(path: Path) -> str | None:
    try:
        return path.read_text(errors="ignore").strip() or None
    except (OSError, PermissionError):
        return None


def collect_hardware() -> dict:
    """Collect a conservative local hardware inventory."""
    cpu = platform.processor() or _read(Path("/proc/cpuinfo"))
    machine = platform.machine()
    system = platform.system()
    release = platform.release()

    memory = None
    meminfo = _read(Path("/proc/meminfo"))
    if meminfo:
        for line in meminfo.splitlines():
            if line.startswith("MemTotal:"):
                memory = line.strip()
                break

    devices = []
    sys_block = Path("/sys/class/block")

    if sys_block.exists():
        try:
            for item in sorted(sys_block.iterdir()):
                devices.append(
                    {
                        "name": item.name,
                        "type": "block",
                    }
                )
        except (OSError, PermissionError):
            import logging; logging.getLogger(__name__).warning('fail-closed %s:%d %s', __file__, 53, _e)

    fingerprint_source = "|".join(
        [
            system,
            release,
            machine,
            cpu or "",
            memory or "",
            ",".join(d["name"] for d in devices),
        ]
    )

    return {
        "platform": {
            "system": system,
            "release": release,
            "machine": machine,
        },
        "cpu": {
            "description": cpu,
            "fingerprint": _hash(cpu or "unknown"),
        },
        "memory": memory,
        "block_devices": devices,
        "fingerprint": _hash(fingerprint_source),
    }


def compare_inventory(previous: dict, current: dict) -> dict:
    """Compare two passive inventories."""
    old_devices = {
        d.get("name")
        for d in previous.get("block_devices", [])
        if isinstance(d, dict)
    }

    new_devices = {
        d.get("name")
        for d in current.get("block_devices", [])
        if isinstance(d, dict)
    }

    return {
        "new_devices": sorted(new_devices - old_devices),
        "removed_devices": sorted(old_devices - new_devices),
        "hardware_changed": (
            previous.get("fingerprint") != current.get("fingerprint")
        ),
    }