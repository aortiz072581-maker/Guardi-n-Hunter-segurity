"""Phase 40 — Defensive Security Operations Center.

Read-only operational aggregation.
No system/network/process mutation is performed.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class SOCStatus:
    status: str
    risk_level: str
    active_incidents: int
    alerts: int
    critical_alerts: int
    evidence_integrity: float
    control_coverage: float
    health: float
    mode: str
    execution_allowed: bool


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_level(risk: float) -> str:
    if risk >= 80:
        return "CRITICAL"
    if risk >= 60:
        return "HIGH"
    if risk >= 30:
        return "MEDIUM"
    return "LOW"


def correlate_alerts(alerts: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create deterministic defensive correlation groups."""
    groups: Dict[str, List[Dict[str, Any]]] = {}

    for alert in alerts:
        asset = str(alert.get("asset", "unknown"))
        category = str(alert.get("category", "unknown"))
        key = f"{asset}:{category}"
        groups.setdefault(key, []).append(dict(alert))

    result = []
    for key, items in sorted(groups.items()):
        result.append(
            {
                "correlation_key": key,
                "count": len(items),
                "assets": sorted(
                    {str(item.get("asset", "unknown")) for item in items}
                ),
                "categories": sorted(
                    {str(item.get("category", "unknown")) for item in items}
                ),
                "mode": "READ_ONLY",
                "execution_allowed": False,
            }
        )

    return result


def build_soc_status(
    *,
    risk_score: float = 0.0,
    active_incidents: int = 0,
    alerts: int = 0,
    critical_alerts: int = 0,
    evidence_integrity: float = 100.0,
    control_coverage: float = 100.0,
    health: float = 100.0,
) -> SOCStatus:
    risk = _number(risk_score)

    values = [
        _number(evidence_integrity),
        _number(control_coverage),
        _number(health),
    ]

    operational = all(value >= 100.0 for value in values) and risk < 80

    return SOCStatus(
        status="OPERATIONAL" if operational else "REVIEW_REQUIRED",
        risk_level=_risk_level(risk),
        active_incidents=int(active_incidents),
        alerts=int(alerts),
        critical_alerts=int(critical_alerts),
        evidence_integrity=max(0.0, min(100.0, values[0])),
        control_coverage=max(0.0, min(100.0, values[1])),
        health=max(0.0, min(100.0, values[2])),
        mode="READ_ONLY",
        execution_allowed=False,
    )


def build_soc_snapshot(
    status: SOCStatus,
    correlations: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "phase": 40,
        "component": "SECURITY_OPERATIONS_CENTER",
        "status": status.status,
        "risk_level": status.risk_level,
        "active_incidents": status.active_incidents,
        "alerts": status.alerts,
        "critical_alerts": status.critical_alerts,
        "evidence_integrity": status.evidence_integrity,
        "control_coverage": status.control_coverage,
        "health": status.health,
        "correlations": list(correlations),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
