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
    if not (r["finding_count"] == 0):
    raise RuntimeError("Assertion failed: r["finding_count"] == 0")
    if not (r["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: r["execution_allowed"] is False")

def test_synthetic_finding():
    r = run_c6_operational(
        sensor_report([simulated_finding()], "FINDINGS")
    )
    if not (r["finding_count"] == 1):
    raise RuntimeError("Assertion failed: r["finding_count"] == 1")
    if not (r["classification_complete"] is False):
    raise RuntimeError("Assertion failed: r["classification_complete"] is False")
    if not (r["correlation"]["findings"][0]["severity"] == "unknown"):
    raise RuntimeError("Assertion failed: r["correlation"]["findings"][0]["severity"] == "unknown"")
    if not (r["automatic_repair"] is False):
    raise RuntimeError("Assertion failed: r["automatic_repair"] is False")
    if not (r["merge_allowed"] is False):
    raise RuntimeError("Assertion failed: r["merge_allowed"] is False")

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
