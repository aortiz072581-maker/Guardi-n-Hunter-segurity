from guardian_hunter.integration.nuclei_diagnostic_adapter import (
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    analyze_nuclei_result,
)


def test_safety_invariants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert RESPONSE_LOCKED is True


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

    assert result["risk"]["max_score"] == 95
    assert result["diagnosis"]["risk_level"] == "CRITICAL"
    assert result["diagnosis"]["problem_detected"] is True
    assert result["containment_recommended"] is True

    assert result["execution_allowed"] is False
    assert result["read_only"] is True
    assert result["dry_run"] is True
    assert result["real_execution_blocked"] is True
    assert result["response_locked"] is True


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

    assert result["status"] == "blocked"
    assert result["findings"] == []
    assert result["diagnosis"] is None
    assert result["containment_recommended"] is False
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True


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

    assert decision is not None
    assert decision["risk_level"] == "CRITICAL"
    assert decision["decision"] == "ESCALATE_FOR_HUMAN_REVIEW"
    assert decision["requires_review"] is True
    assert decision["response_locked"] is True
    assert decision["execution_allowed"] is False

    assert plan is not None
    assert plan["risk_level"] == "CRITICAL"
    assert plan["response_locked"] is True
    assert plan["dry_run"] is True
    assert plan["execution_allowed"] is False
    assert "ESCALATE_FOR_HUMAN_REVIEW" in plan["steps"]
    assert "KEEP_RESPONSE_LOCKED" in plan["steps"]

    assert result["execution_allowed"] is False
    assert result["real_execution_blocked"] is True
    assert result["response_locked"] is True


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

    assert result["status"] == "blocked"
    assert result["diagnosis"] is None
    assert result["decision"] is None
    assert result["response_plan"] is None
    assert result["containment_recommended"] is False
    assert result["execution_allowed"] is False
    assert result["real_execution_blocked"] is True
    assert result["response_locked"] is True
