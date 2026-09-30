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

    assert hw["hardware_changed"] is True
    assert hw["new_devices"] == ["disk1"]
    assert net["addresses_changed"] is True
    assert net["interfaces_changed"] is True
    assert net["routes_changed"] is True

    assert "HARDWARE_CHANGED" in corr["signals"]
    assert "NEW_HARDWARE" in corr["signals"]
    assert "NETWORK_INTERFACE_CHANGED" in corr["signals"]
    assert "ROUTE_CHANGED" in corr["signals"]
    assert corr["risk_hint"] == "high"

    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True
    assert result["response_locked"] is True
    assert result["execution_allowed"] is False


def test_first_observation_has_no_false_drift():
    result = observation.observe_host(
        hardware=NEW_HARDWARE,
        network=NEW_NETWORK,
    )

    assert result["hardware_changes"] == {}
    assert result["network_changes"] == {}
    assert result["correlation"]["signals"] == []
    assert result["correlation"]["risk_hint"] == "normal"
    assert result["execution_allowed"] is False


def test_response_lock_fails_closed(monkeypatch):
    monkeypatch.setattr(observation, "RESPONSE_LOCKED", False)

    assert observation.safety_invariants_hold() is False

    try:
        observation.observe_host(
            hardware=NEW_HARDWARE,
            network=NEW_NETWORK,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Unlocked observation did not fail closed")
