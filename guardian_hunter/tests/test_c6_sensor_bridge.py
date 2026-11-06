import copy
import pytest

from guardian_hunter.integration.c6_sensor_bridge import (
    correlate_sensor_report,
)

def report():
    return {
        "states": {"gitleaks": "FINDINGS", "osv": "CLEAN"},
        "assessment_complete": True,
        "finding_count": 1,
        "human_approval_required": True,
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "findings": [{
            "id": "GH-GITLEAKS-000001",
            "title": "Potential secret: generic-api-key",
            "evidence": ["redacted"],
            "affected_files": ["fixture.json"],
            "execution_allowed": False,
            "automatic_repair": False,
            "merge_allowed": False,
        }],
    }

def test_preserves_id_and_blocks_authority():
    result = correlate_sensor_report(report())
    if not (result["finding_count"] == 1):
    raise RuntimeError("Assertion failed: result["finding_count"] == 1")
    if not (result["findings"][0]["id"] == "GH-GITLEAKS-000001"):
    raise RuntimeError("Assertion failed: result["findings"][0]["id"] == "GH-GITLEAKS-000001"")
    if not (result["findings"][0]["severity"] == "unknown"):
    raise RuntimeError("Assertion failed: result["findings"][0]["severity"] == "unknown"")
    if not (result["classification_complete"] is False):
    raise RuntimeError("Assertion failed: result["classification_complete"] is False")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["automatic_repair"] is False):
    raise RuntimeError("Assertion failed: result["automatic_repair"] is False")
    if not (result["merge_allowed"] is False):
    raise RuntimeError("Assertion failed: result["merge_allowed"] is False")
    if not (result["sha256"]):
    raise RuntimeError("Assertion failed: result["sha256"]")

def test_clean_report():
    r = report()
    r["states"]["gitleaks"] = "CLEAN"
    r["findings"] = []
    r["finding_count"] = 0
    result = correlate_sensor_report(r)
    if not (result["finding_count"] == 0):
    raise RuntimeError("Assertion failed: result["finding_count"] == 0")
    if not (result["classification_complete"] is True):
    raise RuntimeError("Assertion failed: result["classification_complete"] is True")

@pytest.mark.parametrize("mutation", [
    lambda r: r.update(execution_allowed=True),
    lambda r: r.update(assessment_complete=False),
    lambda r: r.update(finding_count=99),
    lambda r: r["findings"][0].update(merge_allowed=True),
    lambda r: r["findings"][0].update(severity="nonsense"),
    lambda r: r["findings"][0].update(id="UNKNOWN"),
    lambda r: r["findings"].append(copy.deepcopy(r["findings"][0])),
    lambda r: r["states"].update(gitleaks="CLEAN"),
])
def test_adversarial_fail_closed(mutation):
    r = report()
    mutation(r)
    with pytest.raises(ValueError):
        correlate_sensor_report(r)
