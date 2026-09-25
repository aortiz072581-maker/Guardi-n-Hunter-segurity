"""Phase 39 — Defensive Security Metrics and Trends."""

from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_metrics(
    *,
    incidents: int = 0,
    alerts: int = 0,
    critical_alerts: int = 0,
    evidence_items: int = 0,
    evidence_verified: int = 0,
    controls_passed: int = 0,
    controls_total: int = 0,
    health_percent: float = 100.0,
) -> dict[str, Any]:
    incidents = max(0, int(incidents))
    alerts = max(0, int(alerts))
    critical_alerts = max(0, int(critical_alerts))
    evidence_items = max(0, int(evidence_items))
    evidence_verified = max(0, int(evidence_verified))
    controls_passed = max(0, int(controls_passed))
    controls_total = max(0, int(controls_total))

    if evidence_items:
        evidence_integrity = round(
            min(evidence_verified, evidence_items)
            / evidence_items
            * 100,
            2,
        )
    else:
        evidence_integrity = 100.0

    if controls_total:
        control_coverage = round(
            min(controls_passed, controls_total)
            / controls_total
            * 100,
            2,
        )
    else:
        control_coverage = 100.0

    health_percent = max(0.0, min(100.0, float(health_percent)))

    return {
        "timestamp": _utc_now(),
        "incidents": incidents,
        "alerts": alerts,
        "critical_alerts": critical_alerts,
        "evidence_items": evidence_items,
        "evidence_integrity_percent": evidence_integrity,
        "control_coverage_percent": control_coverage,
        "health_percent": round(health_percent, 2),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def compare_metrics(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    fields = (
        "incidents",
        "alerts",
        "critical_alerts",
        "evidence_integrity_percent",
        "control_coverage_percent",
        "health_percent",
    )

    changes = {}

    for field in fields:
        old = float(previous.get(field, 0))
        new = float(current.get(field, 0))
        changes[field] = round(new - old, 2)

    return {
        "timestamp": _utc_now(),
        "changes": changes,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def metrics_gate(result: dict[str, Any]) -> bool:
    return (
        result.get("mode") == "READ_ONLY"
        and result.get("execution_allowed") is False
    )
