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
