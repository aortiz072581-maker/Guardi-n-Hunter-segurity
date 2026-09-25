"""Guardian Hunter - hardware/network correlation."""

from __future__ import annotations


def correlate_hardware_network(
    hardware: dict,
    network: dict,
    hardware_changes: dict | None = None,
    network_changes: dict | None = None,
) -> dict:
    """Create correlation signals without taking action."""

    hardware_changes = hardware_changes or {}
    network_changes = network_changes or {}

    signals = []

    if hardware_changes.get("hardware_changed"):
        signals.append("HARDWARE_CHANGED")

    if hardware_changes.get("new_devices"):
        signals.append("NEW_HARDWARE")

    if network_changes.get("interfaces_changed"):
        signals.append("NETWORK_INTERFACE_CHANGED")

    if network_changes.get("routes_changed"):
        signals.append("ROUTE_CHANGED")

    if network_changes.get("neighbors_changed"):
        signals.append("NEIGHBOR_TABLE_CHANGED")

    if network_changes.get("addresses_changed"):
        signals.append("ADDRESS_CHANGED")

    risk_hint = "normal"

    if len(signals) >= 3:
        risk_hint = "high"
    elif len(signals) >= 2:
        risk_hint = "medium"
    elif signals:
        risk_hint = "low"

    return {
        "signals": signals,
        "signal_count": len(signals),
        "risk_hint": risk_hint,
        "hardware_fingerprint": hardware.get("fingerprint"),
        "gateway_count": len(network.get("gateways", [])),
        "neighbor_count": len(network.get("neighbors", [])),
    }
