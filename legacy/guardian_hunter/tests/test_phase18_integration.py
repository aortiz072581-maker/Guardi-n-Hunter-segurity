from guardian_hunter.correlation.network_hardware import (
    correlate_hardware_network,
)
from guardian_hunter.evidence.store import EvidenceStore
from guardian_hunter.network.defense import (
    compare_network_baseline,
)
from guardian_hunter.response import create_incident


hardware = {
    "fingerprint": "abc123",
}

network = {
    "gateways": ["192.168.1.1"],
    "neighbors": [
        {
            "ip": "192.168.1.1",
            "mac": "aa:bb:cc:dd:ee:ff",
        }
    ],
}

hardware_changes = {
    "hardware_changed": True,
    "new_devices": ["wlan-test"],
}

network_changes = {
    "interfaces_changed": True,
    "routes_changed": True,
    "neighbors_changed": False,
    "addresses_changed": False,
}

correlation = correlate_hardware_network(
    hardware,
    network,
    hardware_changes,
    network_changes,
)

assert "HARDWARE_CHANGED" in correlation["signals"]
assert "NETWORK_INTERFACE_CHANGED" in correlation["signals"]
assert "ROUTE_CHANGED" in correlation["signals"]
assert correlation["risk_hint"] == "high"

old = {
    "gateways": ["192.168.1.1"],
    "neighbors": [
        {
            "ip": "192.168.1.1",
            "mac": "aa:bb:cc:dd:ee:ff",
        }
    ],
}

new = {
    "gateways": ["192.168.1.254"],
    "neighbors": [
        {
            "ip": "192.168.1.254",
            "mac": "11:22:33:44:55:66",
        }
    ],
}

changes = compare_network_baseline(old, new)

assert changes["gateway_changed"] is True
assert changes["neighbor_changed"] is True
assert "192.168.1.254" in changes["new_gateways"]

incident = create_incident(
    risk_level="high",
    reason="hardware/network correlation test",
    target="test-target",
    authorized=True,
)

assert incident["containment"]["mode"] == "DRY_RUN"
assert incident["containment"]["executed"] is False
assert incident["verification"]["verified"] is True

store = EvidenceStore(
    "data/test_phase18_incidents.jsonl"
)

record = store.append(
    {
        "incident_id": incident["incident_id"],
        "type": "PHASE18_TEST",
        "correlation": correlation,
    }
)

assert record["incident_id"] == incident["incident_id"]
assert store.count() >= 1

print("NETWORK BASELINE: OK")
print("GATEWAY/ARP SIGNALS: OK")
print("HARDWARE/NETWORK CORRELATION: OK")
print("EVIDENCE STORE: OK")
print("CONTAINMENT STILL DRY-RUN: OK")
print("PHASE 18 INTEGRATION: OK")
