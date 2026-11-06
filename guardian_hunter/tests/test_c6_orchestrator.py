import pytest

from guardian_hunter.integration import c6_orchestrator


def _main():
    return {
        "execution_allowed": False,
        "response_locked": True,
        "status": "review_required",
    }


def _sensor(state="CLEAN", findings=None):
    findings = [] if findings is None else findings
    return {
        "schema": "guardian-security-sensors-v1",
        "states": {"gitleaks": state, "osv": "CLEAN"},
        "finding_count": len(findings),
        "findings": findings,
        "assessment_complete": True,
        "human_approval_required": True,
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
    }


def test_clean_supervised_flow(monkeypatch, tmp_path):
    monkeypatch.setattr(
        c6_orchestrator,
        "run_consolidated_defensive_flow",
        lambda **kwargs: _main(),
    )

    result = c6_orchestrator.run_supervised_flow(
        root=tmp_path,
        baseline_file=tmp_path / "baseline.json",
        sensor_report=_sensor(),
    )

    if not (result["c6_operational"]["finding_count"] == 0):
    raise RuntimeError("Assertion failed: result["c6_operational"]["finding_count"] == 0")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_synthetic_finding(monkeypatch, tmp_path):
    monkeypatch.setattr(
        c6_orchestrator,
        "run_consolidated_defensive_flow",
        lambda **kwargs: _main(),
    )

    finding = {
        "id": "GH-GITLEAKS-SIMULATED",
        "title": "Synthetic credential finding",
        "affected_files": ["synthetic.json"],
        "evidence": ["synthetic evidence only"],
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
    }

    result = c6_orchestrator.run_supervised_flow(
        root=tmp_path,
        baseline_file=tmp_path / "baseline.json",
        sensor_report=_sensor("FINDINGS", [finding]),
    )

    if not (result["c6_operational"]["finding_count"] == 1):
    raise RuntimeError("Assertion failed: result["c6_operational"]["finding_count"] == 1")
    if not (result["c6_operational"]["classification_complete"] is False):
    raise RuntimeError("Assertion failed: result["c6_operational"]["classification_complete"] is False")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")


def test_incomplete_sensor_denied(monkeypatch, tmp_path):
    monkeypatch.setattr(
        c6_orchestrator,
        "run_consolidated_defensive_flow",
        lambda **kwargs: _main(),
    )

    with pytest.raises(ValueError):
        c6_orchestrator.run_supervised_flow(
            root=tmp_path,
            baseline_file=tmp_path / "baseline.json",
            sensor_report=_sensor("ERROR"),
        )


def test_unsafe_main_denied(monkeypatch, tmp_path):
    monkeypatch.setattr(
        c6_orchestrator,
        "run_consolidated_defensive_flow",
        lambda **kwargs: {
            "execution_allowed": True,
            "response_locked": True,
        },
    )

    with pytest.raises(ValueError):
        c6_orchestrator.run_supervised_flow(
            root=tmp_path,
            baseline_file=tmp_path / "baseline.json",
            sensor_report=_sensor(),
        )
