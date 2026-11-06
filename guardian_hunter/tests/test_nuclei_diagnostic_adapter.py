from guardian_hunter.integration.nuclei_diagnostic_adapter import (
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    analyze_nuclei_result,
)


def test_safety_invariants():
    if not (READ_ONLY is True):
    raise RuntimeError("Assertion failed: READ_ONLY is True")
    if not (DRY_RUN is True):
    raise RuntimeError("Assertion failed: DRY_RUN is True")
    if not (REAL_EXECUTION_BLOCKED is True):
    raise RuntimeError("Assertion failed: REAL_EXECUTION_BLOCKED is True")
    if not (RESPONSE_LOCKED is True):
    raise RuntimeError("Assertion failed: RESPONSE_LOCKED is True")


def test_critical_nuclei_finding_reaches_diagnosis():
    result = analyze_nuclei_result(
        {
            "authorized": True,
            "findings": [
                {
                    "category": "vulnerability",
                    "title": "test-critical",
                    "score": 95,
                    "severity": "critical",
                    "confidence": 1.0,
                    "asset_criticality": 1.0,
                    "exposure": 1.0,
                    "evidence": "test",
                    "recommendation": "REVIEW_AND_VALIDATE",
                    "source": "nuclei",
                    "execution_allowed": False,
                    "read_only": True,
                }
            ],
        }
    )

    if not (result["risk"]["max_score"] == 95):
    raise RuntimeError("Assertion failed: result["risk"]["max_score"] == 95")
    if not (result["diagnosis"]["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: result["diagnosis"]["risk_level"] == "CRITICAL"")
    if not (result["diagnosis"]["problem_detected"] is True):
    raise RuntimeError("Assertion failed: result["diagnosis"]["problem_detected"] is True")
    if not (result["containment_recommended"] is True):
    raise RuntimeError("Assertion failed: result["containment_recommended"] is True")

    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["read_only"] is True):
    raise RuntimeError("Assertion failed: result["read_only"] is True")
    if not (result["dry_run"] is True):
    raise RuntimeError("Assertion failed: result["dry_run"] is True")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_unauthorized_result_fails_closed():
    result = analyze_nuclei_result(
        {
            "authorized": False,
            "findings": [
                {
                    "score": 95,
                    "severity": "critical",
                }
            ],
        }
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")
    if not (result["findings"] == []):
    raise RuntimeError("Assertion failed: result["findings"] == []")
    if not (result["diagnosis"] is None):
    raise RuntimeError("Assertion failed: result["diagnosis"] is None")
    if not (result["containment_recommended"] is False):
    raise RuntimeError("Assertion failed: result["containment_recommended"] is False")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_nuclei_decision_and_response_plan_remain_locked():
    result = analyze_nuclei_result(
        {
            "authorized": True,
            "findings": [
                {
                    "category": "vulnerability",
                    "title": "test-critical",
                    "score": 95,
                    "severity": "critical",
                    "confidence": 1.0,
                    "asset_criticality": 1.0,
                    "exposure": 1.0,
                    "evidence": "test",
                    "recommendation": "REVIEW_AND_VALIDATE",
                    "source": "nuclei",
                    "execution_allowed": False,
                    "read_only": True,
                }
            ],
        }
    )

    decision = result["decision"]
    plan = result["response_plan"]

    if not (decision is not None):
    raise RuntimeError("Assertion failed: decision is not None")
    if not (decision["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: decision["risk_level"] == "CRITICAL"")
    if not (decision["decision"] == "ESCALATE_FOR_HUMAN_REVIEW"):
    raise RuntimeError("Assertion failed: decision["decision"] == "ESCALATE_FOR_HUMAN_REVIEW"")
    if not (decision["requires_review"] is True):
    raise RuntimeError("Assertion failed: decision["requires_review"] is True")
    if not (decision["response_locked"] is True):
    raise RuntimeError("Assertion failed: decision["response_locked"] is True")
    if not (decision["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: decision["execution_allowed"] is False")

    if not (plan is not None):
    raise RuntimeError("Assertion failed: plan is not None")
    if not (plan["risk_level"] == "CRITICAL"):
    raise RuntimeError("Assertion failed: plan["risk_level"] == "CRITICAL"")
    if not (plan["response_locked"] is True):
    raise RuntimeError("Assertion failed: plan["response_locked"] is True")
    if not (plan["dry_run"] is True):
    raise RuntimeError("Assertion failed: plan["dry_run"] is True")
    if not (plan["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: plan["execution_allowed"] is False")
    if not ("ESCALATE_FOR_HUMAN_REVIEW" in plan["steps"]):
    raise RuntimeError("Assertion failed: "ESCALATE_FOR_HUMAN_REVIEW" in plan["steps"]")
    if not ("KEEP_RESPONSE_LOCKED" in plan["steps"]):
    raise RuntimeError("Assertion failed: "KEEP_RESPONSE_LOCKED" in plan["steps"]")

    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")


def test_unauthorized_nuclei_never_creates_decision_or_plan():
    result = analyze_nuclei_result(
        {
            "authorized": False,
            "findings": [
                {
                    "score": 100,
                    "severity": "critical",
                }
            ],
        }
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")
    if not (result["diagnosis"] is None):
    raise RuntimeError("Assertion failed: result["diagnosis"] is None")
    if not (result["decision"] is None):
    raise RuntimeError("Assertion failed: result["decision"] is None")
    if not (result["response_plan"] is None):
    raise RuntimeError("Assertion failed: result["response_plan"] is None")
    if not (result["containment_recommended"] is False):
    raise RuntimeError("Assertion failed: result["containment_recommended"] is False")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["real_execution_blocked"] is True):
    raise RuntimeError("Assertion failed: result["real_execution_blocked"] is True")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
