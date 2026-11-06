from guardian_hunter.integration import passive_host_observation as observation


OLD_HARDWARE = {
    "fingerprint": "old",
    "block_devices": [{"name": "disk0"}],
}

NEW_HARDWARE = {
    "fingerprint": "new",
    "block_devices": [
        {"name": "disk0"},
        {"name": "disk1"},
    ],
}

OLD_NETWORK = {
    "hostname": "test-host",
    "addresses": ["127.0.0.1"],
    "interfaces": "lo UP",
    "routes": "",
    "neighbors": "",
}

NEW_NETWORK = {
    "hostname": "test-host",
    "addresses": ["127.0.0.1", "192.0.2.10"],
    "interfaces": "lo UP\neth0 UP",
    "routes": "default via 192.0.2.1",
    "neighbors": "",
}


def test_passive_observation_contract():
    result = observation.observe_host(
        OLD_HARDWARE,
        OLD_NETWORK,
        hardware=NEW_HARDWARE,
        network=NEW_NETWORK,
    )

    hw = result["hardware_changes"]
    net = result["network_changes"]
    corr = result["correlation"]

    if not (hw["hardware_changed"] is True):
    raise RuntimeError("Assertion failed: hw["hardware_changed"] is True")
    if not (hw["new_devices"] == ["disk1"]):
    raise RuntimeError("Assertion failed: hw["new_devices"] == ["disk1"]")
    if not (net["addresses_changed"] is True):
    raise RuntimeError("Assertion failed: net["addresses_changed"] is True")
    if not (net["interfaces_changed"] is True):
    raise RuntimeError("Assertion failed: net["interfaces_changed"] is True")
    if not (net["routes_changed"] is True):
    raise RuntimeError("Assertion failed: net["routes_changed"] is True")

    if not ("HARDWARE_CHANGED" in corr["signals"]):
    raise RuntimeError("Assertion failed: "HARDWARE_CHANGED" in corr["signals"]")
    if not ("NEW_HARDWARE" in corr["signals"]):
    raise RuntimeError("Assertion failed: "NEW_HARDWARE" in corr["signals"]")
    if not ("NETWORK_INTERFACE_CHANGED" in corr["signals"]):
    raise RuntimeError("Assertion failed: "NETWORK_INTERFACE_CHANGED" in corr["signals"]")
    if not ("ROUTE_CHANGED" in corr["signals"]):
    raise RuntimeError("Assertion failed: "ROUTE_CHANGED" in corr["signals"]")
    if not (corr["risk_hint"] == "high"):
    raise RuntimeError("Assertion failed: corr["risk_hint"] == "high"")

    if not (result["read_only"] is True):
    raise RuntimeError("Assertion failed: result["read_only"] is True")
    if not (result["dry_run"] is True):
    raise RuntimeError("Assertion failed: result["dry_run"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["human_review_required"] is True):
    raise RuntimeError("Assertion failed: result["human_review_required"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")


def test_first_observation_has_no_false_drift():
    result = observation.observe_host(
        hardware=NEW_HARDWARE,
        network=NEW_NETWORK,
    )

    if not (result["hardware_changes"] == {}):
    raise RuntimeError("Assertion failed: result["hardware_changes"] == {}")
    if not (result["network_changes"] == {}):
    raise RuntimeError("Assertion failed: result["network_changes"] == {}")
    if not (result["correlation"]["signals"] == []):
    raise RuntimeError("Assertion failed: result["correlation"]["signals"] == []")
    if not (result["correlation"]["risk_hint"] == "normal"):
    raise RuntimeError("Assertion failed: result["correlation"]["risk_hint"] == "normal"")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")


def test_response_lock_fails_closed(monkeypatch):
    monkeypatch.setattr(observation, "RESPONSE_LOCKED", False)

    if not (observation.safety_invariants_hold() is False):
    raise RuntimeError("Assertion failed: observation.safety_invariants_hold() is False")

    try:
        observation.observe_host(
            hardware=NEW_HARDWARE,
            network=NEW_NETWORK,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Unlocked observation did not fail closed")
