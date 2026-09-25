"""Phase 29 — Advanced Defensive Reporting
Produces structured technical/executive reports without executing actions.
"""

from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def build_report(
    *,
    dashboard=None,
    decisions=None,
    timeline=None,
    evidence=None,
    response=None,
    baseline=None,
):
    dashboard = dashboard or {}
    decisions = decisions or []
    timeline = timeline or []
    evidence = evidence or []
    response = response or {}
    baseline = baseline or {}

    return {
        "report": "GUARDIAN_HUNTER_ADVANCED",
        "generated_at": _utc_now(),
        "mode": "READ_ONLY",
        "execution_allowed": False,
        "technical": {
            "risk": dashboard.get("risk", {}),
            "alerts": dashboard.get("alerts", []),
            "incidents": dashboard.get("incidents", []),
            "health": dashboard.get("health", {}),
            "baseline": baseline,
            "response": response,
        },
        "executive": {
            "risk_score": dashboard.get("risk", {}).get("score"),
            "health_state": dashboard.get("health", {}).get("state"),
            "incident_count": len(dashboard.get("incidents", [])),
            "alert_count": len(dashboard.get("alerts", [])),
            "evidence_count": len(evidence),
        },
        "timeline": timeline,
        "decisions": decisions,
        "evidence": evidence,
        "integrity": {
            "baseline": baseline.get("integrity", "UNKNOWN"),
            "evidence_present": bool(evidence),
        },
        "response_status": response,
        "security": {
            "dry_run": True,
            "execution_locked": True,
        },
    }


def technical_summary(report):
    """Return technical report summary."""
    technical = report.get("technical", {})

    return {
        "risk": technical.get("risk", {}),
        "alerts": len(technical.get("alerts", [])),
        "incidents": len(technical.get("incidents", [])),
        "health": technical.get("health", {}),
        "baseline": technical.get("baseline", {}),
        "response": technical.get("response", {}),
    }


def executive_summary(report):
    """Return concise executive summary."""
    return {
        "generated_at": report.get("generated_at"),
        "risk_score": report.get("executive", {}).get("risk_score"),
        "health_state": report.get("executive", {}).get("health_state"),
        "incident_count": report.get("executive", {}).get("incident_count", 0),
        "alert_count": report.get("executive", {}).get("alert_count", 0),
        "evidence_count": report.get("executive", {}).get("evidence_count", 0),
        "execution_allowed": report.get("execution_allowed", False),
        "mode": report.get("mode"),
    }


def verify_report(report):
    """Verify report safety invariants."""
    security = report.get("security", {})

    valid = (
        report.get("report") == "GUARDIAN_HUNTER_ADVANCED"
        and report.get("mode") == "READ_ONLY"
        and report.get("execution_allowed") is False
        and security.get("dry_run") is True
        and security.get("execution_locked") is True
    )

    return {
        "valid": valid,
        "mode": report.get("mode"),
        "execution_locked": True,
    }
