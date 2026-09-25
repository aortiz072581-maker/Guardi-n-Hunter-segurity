"""Phase 28 — Dashboard Pro
Defensive read-only aggregation layer.
"""

from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def build_dashboard(
    *,
    system=None,
    risk=None,
    alerts=None,
    incidents=None,
    evidence=None,
    baseline=None,
    health=None,
    response=None,
):
    """Build a read-only dashboard snapshot."""
    return {
        "dashboard": "GUARDIAN_HUNTER_PRO",
        "generated_at": _utc_now(),
        "mode": "READ_ONLY",
        "execution_allowed": False,
        "system": system or {},
        "risk": risk or {},
        "alerts": alerts or [],
        "incidents": incidents or [],
        "evidence": evidence or [],
        "baseline": baseline or {},
        "health": health or {},
        "response": response or {},
        "security": {
            "dry_run": True,
            "execution_locked": True,
            "rollback_required_for_stateful_changes": True,
        },
    }


def dashboard_summary(dashboard):
    """Return compact dashboard status."""
    health = dashboard.get("health", {})
    response = dashboard.get("response", {})

    return {
        "generated_at": dashboard.get("generated_at"),
        "mode": dashboard.get("mode"),
        "execution_allowed": dashboard.get("execution_allowed", False),
        "health_state": health.get("state", "UNKNOWN"),
        "response_state": response.get("state", "UNKNOWN"),
        "risk_score": dashboard.get("risk", {}).get("score"),
        "alerts_count": len(dashboard.get("alerts", [])),
        "incidents_count": len(dashboard.get("incidents", [])),
        "evidence_count": len(dashboard.get("evidence", [])),
        "baseline_integrity": dashboard.get("baseline", {}).get(
            "integrity", "UNKNOWN"
        ),
    }


def verify_dashboard(dashboard):
    """Verify dashboard safety invariants."""
    required = {
        "dashboard",
        "generated_at",
        "mode",
        "execution_allowed",
        "system",
        "risk",
        "alerts",
        "incidents",
        "evidence",
        "baseline",
        "health",
        "response",
        "security",
    }

    missing = required.difference(dashboard.keys())

    safe = (
        not missing
        and dashboard.get("mode") == "READ_ONLY"
        and dashboard.get("execution_allowed") is False
        and dashboard.get("security", {}).get("dry_run") is True
        and dashboard.get("security", {}).get("execution_locked") is True
    )

    return {
        "valid": safe,
        "missing": sorted(missing),
        "execution_locked": True,
        "mode": "READ_ONLY",
    }
