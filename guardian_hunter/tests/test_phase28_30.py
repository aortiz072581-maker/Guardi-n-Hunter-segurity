"""Phase 28-30 validation tests."""

from guardian_hunter.dashboard.phase28 import (
    build_dashboard,
    dashboard_summary,
    verify_dashboard,
)

from guardian_hunter.reports.phase29 import (
    build_report,
    technical_summary,
    executive_summary,
    verify_report,
)


def test_phase28():
    dashboard = build_dashboard(
        system={"status": "ONLINE"},
        risk={"score": 42},
        alerts=[{"id": "A1"}],
        incidents=[{"id": "I1"}],
        evidence=[{"hash": "abc"}],
        baseline={"integrity": "VALID"},
        health={"state": "HEALTHY"},
        response={"state": "PLANNED"},
    )

    summary = dashboard_summary(dashboard)
    verification = verify_dashboard(dashboard)

    assert summary["risk_score"] == 42
    assert summary["alerts_count"] == 1
    assert summary["incidents_count"] == 1
    assert summary["evidence_count"] == 1
    assert verification["valid"] is True
    assert dashboard["execution_allowed"] is False

    print("PHASE 28 DASHBOARD PRO: OK")
    print("PHASE 28 READ-ONLY GATE: OK")


def test_phase29():
    dashboard = build_dashboard(
        risk={"score": 65},
        alerts=[{"id": "A1"}],
        incidents=[{"id": "I1"}],
        evidence=[{"hash": "abc"}],
        baseline={"integrity": "VALID"},
        health={"state": "HEALTHY"},
        response={"state": "PLANNED"},
    )

    report = build_report(
        dashboard=dashboard,
        decisions=[{"priority": "HIGH"}],
        timeline=[{"sequence": 1}],
        evidence=[{"hash": "abc"}],
        response={"state": "PLANNED"},
        baseline={"integrity": "VALID"},
    )

    technical = technical_summary(report)
    executive = executive_summary(report)
    verification = verify_report(report)

    assert technical["risk"]["score"] == 65
    assert executive["risk_score"] == 65
    assert executive["incident_count"] == 1
    assert verification["valid"] is True
    assert report["execution_allowed"] is False

    print("PHASE 29 ADVANCED REPORTING: OK")
    print("PHASE 29 REPORT INTEGRITY: OK")


def test_phase30():
    dashboard = build_dashboard()
    report = build_report(dashboard=dashboard)

    assert verify_dashboard(dashboard)["valid"] is True
    assert verify_report(report)["valid"] is True

    assert dashboard["security"]["dry_run"] is True
    assert dashboard["security"]["execution_locked"] is True

    assert report["security"]["dry_run"] is True
    assert report["security"]["execution_locked"] is True

    print("PHASE 30 SECURITY VALIDATION: OK")
    print("PHASE 30 EXECUTION LOCK: OK")
    print("PHASE 30 DRY-RUN: OK")


if __name__ == "__main__":
    test_phase28()
    test_phase29()
    test_phase30()
    print("PHASE 28-30 TEST: OK")
