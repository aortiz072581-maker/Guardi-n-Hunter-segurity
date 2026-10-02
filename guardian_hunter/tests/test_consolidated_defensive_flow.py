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

    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True
    assert result["response_locked"] is True
    assert result["execution_allowed"] is False

    assert "hardware" in result
    assert "network" in result
    assert "correlation" in result
    assert "diagnosis" in result
    assert "integrity_tamper" in result
    assert "evidence" in result

    protection = result["integrity_tamper"]
    assert protection["integrity_state"] == "INTEGRITY_OK"
    assert protection["integrity_fail_closed"] is True
    assert protection["tamper_fail_closed"] is True
    assert protection["execution_allowed"] is False
    assert protection["response_locked"] is True

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

    assert result["status"] == "blocked"
    assert result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"
    assert result["integrity_tamper"]["modified"]
    assert "integrity" in result["diagnosis"]["categories"]
    assert result["diagnosis"]["risk_level"] == "CRITICAL"
    assert "PROTECTED_FILE_INTEGRITY_CHANGE" in result["diagnosis"]["probable_causes"]

    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True

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

    assert result["status"] == "blocked"

    signals = result["correlation"]["signals"]
    assert "HARDWARE_CHANGED" in signals
    assert "NEW_HARDWARE" in signals
    assert "NETWORK_INTERFACE_CHANGED" in signals
    assert "ROUTE_CHANGED" in signals

    categories = result["diagnosis"]["categories"]
    assert "hardware" in categories
    assert "network" in categories
    assert "integrity" in categories

    assert result["diagnosis"]["risk_level"] == "CRITICAL"
    assert result["integrity_tamper"]["integrity_state"] == "TAMPER_DETECTED"

    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True


def test_consolidated_recovery_stays_planning_only():
    root = Path.cwd()
    baseline = root / "data" / "integrity_baseline.json"

    result = run_consolidated_defensive_flow(
        root=root,
        baseline_file=baseline,
        hardware={},
        network={},
    )

    assert "recovery" in result

    recovery = result["recovery"]

    assert "incident" in recovery
    assert "plan" in recovery
    assert "review" in recovery

    # Recovery 6.3/6.4 may plan and review,
    # but must never execute automatically.
    assert recovery["automatic_recovery"] is False
    assert recovery["execution_allowed"] is False
    assert recovery["response_locked"] is True

    # Global fail-closed guarantees must remain intact.
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
    assert result["real_execution_blocked"] is True
    assert result["human_review_required"] is True

    recovery = result["recovery"]
    assert recovery["automatic_recovery"] is False
    assert recovery["execution_allowed"] is False
    assert recovery["response_locked"] is True
