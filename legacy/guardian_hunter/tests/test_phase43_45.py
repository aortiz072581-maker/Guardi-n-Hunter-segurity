"""Tests for phases 43-45."""

from guardian_hunter.cases.manager import (
    attach_alerts,
    attach_evidence,
    build_case_record,
    create_case,
    transition_case,
    validate_case,
)
from guardian_hunter.risk_analytics.engine import (
    aggregate_risk_history,
    build_risk_report,
    calculate_risk_analytics,
    compare_risk_scores,
)
from guardian_hunter.readiness.assessment import (
    assess_readiness,
    build_readiness_report,
    build_readiness_summary,
    readiness_gate,
    validate_readiness_contract,
)


def main():
    # ==================================================
    # PHASE 43
    # ==================================================

    case = create_case(
        "CASE-43",
        "Defensive network investigation",
        severity="HIGH",
        asset="phone",
    )

    attach_evidence(case, ["EV-1", "EV-2", "EV-2"])
    attach_alerts(case, ["AL-1", "AL-2"])

    transition_case(
        case,
        "INVESTIGATING",
        reason="Evidence review started",
    )

    assert validate_case(case) is True
    assert case.evidence_ids == ["EV-1", "EV-2"]
    assert case.alert_ids == ["AL-1", "AL-2"]
    assert case.execution_allowed is False

    record = build_case_record(case)

    assert record["phase"] == 43
    assert record["mode"] == "READ_ONLY"
    assert record["execution_allowed"] is False

    print("PHASE 43 SECURITY CASE MANAGEMENT: OK")
    print("PHASE 43 CASE STATE: OK")
    print("PHASE 43 EVIDENCE/ALERT LINKS: OK")
    print("PHASE 43 READ-ONLY: OK")

    # ==================================================
    # PHASE 44
    # ==================================================

    analytics = calculate_risk_analytics(
        severity="HIGH",
        confidence=90,
        evidence_count=4,
        alert_count=6,
        critical_alerts=1,
        previous_score=40,
    )

    assert 0.0 <= analytics.risk_score <= 100.0
    assert analytics.execution_allowed is False
    assert analytics.trend in {
        "INCREASING",
        "DECREASING",
        "STABLE",
    }

    report = build_risk_report(analytics)

    assert report["phase"] == 44
    assert report["execution_allowed"] is False

    comparison = compare_risk_scores(analytics.risk_score, 40)

    assert comparison["execution_allowed"] is False

    history = aggregate_risk_history([20, 35, 50, analytics.risk_score])

    assert history["count"] == 4
    assert history["execution_allowed"] is False

    print("PHASE 44 ADVANCED RISK ANALYTICS: OK")
    print("PHASE 44 RISK FACTORS: OK")
    print("PHASE 44 TREND ANALYSIS: OK")
    print("PHASE 44 READ-ONLY: OK")

    # ==================================================
    # PHASE 45
    # ==================================================

    controls = {
        "policy_guard": True,
        "audit_integrity": True,
        "evidence_integrity": True,
        "baseline_integrity": True,
        "health_monitor": True,
        "response_lock": True,
    }

    readiness = assess_readiness(controls)

    assert readiness.readiness == "READY"
    assert readiness.score == 100.0
    assert readiness.failed_controls == 0
    assert readiness.execution_allowed is False
    assert validate_readiness_contract(readiness) is True
    assert readiness_gate(readiness) is False

    readiness_report = build_readiness_report(readiness)

    assert readiness_report["phase"] == 45
    assert readiness_report["execution_allowed"] is False

    summary = build_readiness_summary([readiness])

    assert summary["assessments"] == 1
    assert summary["average_score"] == 100.0
    assert summary["execution_allowed"] is False

    print("PHASE 45 DEFENSIVE READINESS: OK")
    print("PHASE 45 CONTROL ASSESSMENT: OK")
    print("PHASE 45 READINESS GATE: OK")
    print("PHASE 45 READ-ONLY: OK")
    print("PHASE 43-45 TEST: OK")


if __name__ == "__main__":
    main()
