"""Passive local hardware/network observation.

Observes local state, compares snapshots, and correlates defensive
signals. It never performs a response action.
"""

from __future__ import annotations

from guardian_hunter.correlation.network_hardware import (
    correlate_hardware_network,
)
from guardian_hunter.hardware.detector import (
    collect_hardware,
    compare_inventory,
)
from guardian_hunter.network.inventory import (
    collect_network_inventory,
    detect_network_changes,
)

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


def safety_invariants_hold() -> bool:
    return all((
        READ_ONLY,
        DRY_RUN,
        REAL_EXECUTION_BLOCKED,
        HUMAN_REVIEW_REQUIRED,
        RESPONSE_LOCKED,
    ))


def observe_host(
    previous_hardware: dict | None = None,
    previous_network: dict | None = None,
    *,
    hardware: dict | None = None,
    network: dict | None = None,
) -> dict:
    """Observe and correlate local state without taking action."""

    if not safety_invariants_hold():
        raise RuntimeError(
            "Passive observation safety invariants are not satisfied"
        )

    current_hardware = (
        dict(hardware)
        if hardware is not None
        else collect_hardware()
    )

    current_network = (
        dict(network)
        if network is not None
        else collect_network_inventory()
    )

    hardware_changes = (
        compare_inventory(previous_hardware, current_hardware)
        if previous_hardware is not None
        else {}
    )

    network_changes = (
        detect_network_changes(previous_network, current_network)
        if previous_network is not None
        else {}
    )

    correlation = correlate_hardware_network(
        current_hardware,
        current_network,
        hardware_changes,
        network_changes,
    )

    return {
        "hardware": current_hardware,
        "network": current_network,
        "hardware_changes": hardware_changes,
        "network_changes": network_changes,
        "correlation": correlation,
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "human_review_required": True,
        "response_locked": True,
        "execution_allowed": False,
    }
