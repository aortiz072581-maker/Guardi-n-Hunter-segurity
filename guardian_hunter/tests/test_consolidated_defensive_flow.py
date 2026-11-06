from pathlib import Path

from guardian_hunter.integration.consolidated_defensive_flow import (
    run_consolidated_defensive_flow,
)


def test_consolidated_flow_stays_fail_closed():
    root = Path.cwd()
    baseline = root / "data" / "integrity_baseline.json"

    result = run_consolidated_defensive_flow(
        root=root,
        baseline_file=baseline,
        hardware={},
        network={},
    )

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

    if not ("hardware" in result):
    raise RuntimeError("Assertion failed: "hardware" in result")
    if not ("network" in result):
    raise RuntimeError("Assertion failed: "network" in result")
    if not ("correlation" in result):
    raise RuntimeError("Assertion failed: "correlation" in result")
    if not ("diagnosis" in result):
    raise RuntimeError("Assertion failed: "diagnosis" in result")
    if not ("integrity_tamper" in result):
    raise RuntimeError("Assertion failed: "integrity_tamper" in result")
    if not ("evidence" in result):
    raise RuntimeError("Assertion failed: "evidence" in result")

    protection = result["integrity_tamper"]
    if not (protection["integrity_state"] == "INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: protection["integrity_state"] == "INTEGRITY_OK"")
    if not (protection["integrity_fail_closed"] is True):
    raise RuntimeError("Assertion failed: protection["integrity_fail_closed"] is True")
    if not (protection["tamper_fail_closed"] is True):
    raise RuntimeError("Assertion failed: protection["tamper_fail_closed"] is True")
    if not (protection["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: protection["execution_allowed"] is False")
    if not (protection["response_locked"] is True):
    raise RuntimeError("Assertion failed: protection["response_locked"] is True")

def test_consolidated_flow_blocks_integrity_change(tmp_path):
    import json
    from guardian_hunter.integrity.self_integrity import (
        baseline_to_dict,
        build_baseline,
    )

    protected = (
        tmp_path
        / "guardian_hunter"
        / "authorization"
        / "sample.py"
    )
    protected.parent.mkdir(parents=True)
    protected.write_text("SAFE = True\n")

    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(
        baseline_to_dict(build_baseline(tmp_path))
    ))

    protected.write_text("SAFE = False\n")

    result = run_consolidated_defensive_flow(
        root=tmp_path,
        baseline_file=baseline,
        hardware={},
        network={},
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")
    if not (result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"")
    if not (result["integrity_tamper"]["modified"]):
    raise RuntimeError("Assertion failed: result["integrity_tamper"]["modified"]")
    if not ("integrity" in result["diagnosis"]["categories"]):
    raise RuntimeError("Assertion failed: "integrity" in result["diagnosis"]["categories"]")
    if not (result["diagnosis"]["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: result["diagnosis"]["risk_level"] == "CRITICAL"")
    if not ("PROTECTED_FILE_INTEGRITY_CHANGE" in result["diagnosis"]["probable_causes"]):
    raise RuntimeError("Assertion failed: "PROTECTED_FILE_INTEGRITY_CHANGE" in result["diagnosis"]["probable_causes"]")

    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["human_review_required"] is True):
    raise RuntimeError("Assertion failed: result["human_review_required"] is True")

def test_consolidated_flow_correlates_multiple_defenses(tmp_path):
    import json
    from guardian_hunter.integrity.self_integrity import (
        baseline_to_dict,
        build_baseline,
    )

    protected = (
        tmp_path
        / "guardian_hunter"
        / "authorization"
        / "sample.py"
    )
    protected.parent.mkdir(parents=True)
    protected.write_text("SAFE = True\n")

    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps(
        baseline_to_dict(build_baseline(tmp_path))
    ))

    protected.write_text("SAFE = False\n")

    previous_hardware = {
        "fingerprint": "old",
        "block_devices": [{"name": "old-device"}],
    }
    hardware = {
        "fingerprint": "new",
        "block_devices": [{"name": "new-device"}],
    }

    previous_network = {
        "addresses": ["old"],
        "interfaces": "old",
        "routes": "old",
        "neighbors": "old",
    }
    network = {
        "addresses": ["new"],
        "interfaces": "new",
        "routes": "new",
        "neighbors": "new",
        "gateways": [],
    }

    result = run_consolidated_defensive_flow(
        root=tmp_path,
        baseline_file=baseline,
        previous_hardware=previous_hardware,
        previous_network=previous_network,
        hardware=hardware,
        network=network,
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")

    signals = result["correlation"]["signals"]
    if not ("HARDWARE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "HARDWARE_CHANGED" in signals")
    if not ("NEW_HARDWARE" in signals):
    raise RuntimeError("Assertion failed: "NEW_HARDWARE" in signals")
    if not ("NETWORK_INTERFACE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "NETWORK_INTERFACE_CHANGED" in signals")
    if not ("ROUTE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "ROUTE_CHANGED" in signals")

    categories = result["diagnosis"]["categories"]
    if not ("hardware" in categories):
    raise RuntimeError("Assertion failed: "hardware" in categories")
    if not ("network" in categories):
    raise RuntimeError("Assertion failed: "network" in categories")
    if not ("integrity" in categories):
    raise RuntimeError("Assertion failed: "integrity" in categories")

    if not (result["diagnosis"]["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: result["diagnosis"]["risk_level"] == "CRITICAL"")
    if not (result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"")

    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["human_review_required"] is True):
    raise RuntimeError("Assertion failed: result["human_review_required"] is True")


def test_consolidated_recovery_stays_planning_only():
    root = Path.cwd()
    baseline = root / "data" / "integrity_baseline.json"

    result = run_consolidated_defensive_flow(
        root=root,
        baseline_file=baseline,
        hardware={},
        network={},
    )

    if not ("recovery" in result):
    raise RuntimeError("Assertion failed: "recovery" in result")

    recovery = result["recovery"]

    if not ("incident" in recovery):
    raise RuntimeError("Assertion failed: "incident" in recovery")
    if not ("plan" in recovery):
    raise RuntimeError("Assertion failed: "plan" in recovery")
    if not ("review" in recovery):
    raise RuntimeError("Assertion failed: "review" in recovery")

    # Recovery 6.3/6.4 may plan and review,
    # but must never execute automatically.
    if not (recovery["automatic_recovery"] is False):
    raise RuntimeError("Assertion failed: recovery["automatic_recovery"] is False")
    if not (recovery["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: recovery["execution_allowed"] is False")
    if not (recovery["response_locked"] is True):
    raise RuntimeError("Assertion failed: recovery["response_locked"] is True")

    # Global fail-closed guarantees must remain intact.
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["human_review_required"] is True):
    raise RuntimeError("Assertion failed: result["human_review_required"] is True")

    recovery = result["recovery"]
    if not (recovery["automatic_recovery"] is False):
    raise RuntimeError("Assertion failed: recovery["automatic_recovery"] is False")
    if not (recovery["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: recovery["execution_allowed"] is False")
    if not (recovery["response_locked"] is True):
    raise RuntimeError("Assertion failed: recovery["response_locked"] is True")



def test_consolidated_sensor_pipeline_is_fail_closed(tmp_path):
    import json

    from guardian_hunter.integrity.self_integrity import (
        baseline_to_dict,
        build_baseline,
    )

    protected = (
        tmp_path
        / "guardian_hunter"
        / "authorization"
        / "sample.py"
    )
    protected.parent.mkdir(parents=True)
    protected.write_text("SAFE = True\n")

    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            baseline_to_dict(build_baseline(tmp_path))
        )
    )

    previous_hardware = {
        "fingerprint": "HW-OLD",
        "block_devices": [],
    }
    current_hardware = {
        "fingerprint": "HW-NEW",
        "block_devices": [{"name": "new-device"}],
    }

    previous_network = {
        "addresses": ["10.0.0.2"],
        "interfaces": "old-interface",
        "routes": "old-route",
        "neighbors": "old-neighbor",
        "gateways": [],
    }
    current_network = {
        "addresses": ["10.0.0.3"],
        "interfaces": "new-interface",
        "routes": "new-route",
        "neighbors": "new-neighbor",
        "gateways": ["10.0.0.1"],
    }

    result = run_consolidated_defensive_flow(
        root=tmp_path,
        baseline_file=baseline,
        previous_hardware=previous_hardware,
        previous_network=previous_network,
        hardware=current_hardware,
        network=current_network,
    )

    # Sensor observations reach the consolidated flow.
    if not (result["hardware"] == current_hardware):
    raise RuntimeError("Assertion failed: result["hardware"] == current_hardware")
    if not (result["network"] == current_network):
    raise RuntimeError("Assertion failed: result["network"] == current_network")

    # Changes are detected and correlated.
    if not (result["hardware_changes"]["hardware_changed"] is True):
    raise RuntimeError("Assertion failed: result["hardware_changes"]["hardware_changed"] is True")
    if not (result["network_changes"]["interfaces_changed"] is True):
    raise RuntimeError("Assertion failed: result["network_changes"]["interfaces_changed"] is True")
    if not (result["network_changes"]["routes_changed"] is True):
    raise RuntimeError("Assertion failed: result["network_changes"]["routes_changed"] is True")

    signals = result["correlation"]["signals"]
    if not ("HARDWARE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "HARDWARE_CHANGED" in signals")
    if not ("NETWORK_INTERFACE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "NETWORK_INTERFACE_CHANGED" in signals")
    if not ("ROUTE_CHANGED" in signals):
    raise RuntimeError("Assertion failed: "ROUTE_CHANGED" in signals")

    # The complete pipeline remains fail-closed.
    if not (result["read_only"] is True):
    raise RuntimeError("Assertion failed: result["read_only"] is True")
    if not (result["dry_run"] is True):
    raise RuntimeError("Assertion failed: result["dry_run"] is True")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["human_review_required"] is True):
    raise RuntimeError("Assertion failed: result["human_review_required"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")

    recovery = result["recovery"]
    if not (recovery["automatic_recovery"] is False):
    raise RuntimeError("Assertion failed: recovery["automatic_recovery"] is False")
    if not (recovery["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: recovery["execution_allowed"] is False")
    if not (recovery["response_locked"] is True):
    raise RuntimeError("Assertion failed: recovery["response_locked"] is True")
