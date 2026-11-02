import pytest

from guardian_hunter.integration.c6_operational import (
    run_c6_operational,
)

def sensor_report(findings=None, state="CLEAN"):
    findings = [] if findings is None else findings
    return {
        "states": {"gitleaks": state, "osv": "CLEAN"},
        "assessment_complete": True,
        "finding_count": len(findings),
        "human_approval_required": True,
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "findings": findings,
    }

def simulated_finding():
    return {
        "id": "GH-GITLEAKS-SIMULATED",
        "title": "Synthetic credential finding",
        "evidence": ["synthetic evidence only"],
        "affected_files": ["synthetic.json"],
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
    }

def test_clean():
    r = run_c6_operational(sensor_report())
    assert r["finding_count"] == 0
    assert r["execution_allowed"] is False

def test_synthetic_finding():
    r = run_c6_operational(
        sensor_report([simulated_finding()], "FINDINGS")
    )
    assert r["finding_count"] == 1
    assert r["classification_complete"] is False
    assert r["correlation"]["findings"][0]["severity"] == "unknown"
    assert r["automatic_repair"] is False
    assert r["merge_allowed"] is False

def test_unsafe_authority_denied():
    r = sensor_report()
    r["execution_allowed"] = True
    with pytest.raises(ValueError):
        run_c6_operational(r)

def test_invalid_sensor_denied():
    r = sensor_report()
    r["states"]["gitleaks"] = "ERROR"
    with pytest.raises(ValueError):
        run_c6_operational(r)
