"""Phase 44 — Defensive Advanced Risk Analytics.

Calculates explainable risk factors and trends.
It does not trigger or execute response actions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class RiskAnalytics:
    risk_score: float
    severity_factor: float
    confidence_factor: float
    evidence_factor: float
    alert_factor: float
    trend: str
    explanation: List[str]
    mode: str
    execution_allowed: bool


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def calculate_risk_analytics(
    *,
    severity: str = "LOW",
    confidence: float = 0.0,
    evidence_count: int = 0,
    alert_count: int = 0,
    critical_alerts: int = 0,
    previous_score: float = 0.0,
) -> RiskAnalytics:
    severity_weights = {
        "CRITICAL": 100.0,
        "HIGH": 75.0,
        "MEDIUM": 50.0,
        "LOW": 20.0,
    }

    severity_factor = severity_weights.get(
        str(severity).upper(),
        0.0,
    )

    confidence_factor = _clamp(_number(confidence))
    evidence_factor = min(max(int(evidence_count), 0) * 5.0, 25.0)
    alert_factor = min(max(int(alert_count), 0) * 3.0, 20.0)
    critical_factor = min(max(int(critical_alerts), 0) * 10.0, 30.0)

    score = (
        severity_factor * 0.40
        + confidence_factor * 0.25
        + evidence_factor * 0.10
        + alert_factor * 0.10
        + critical_factor * 0.15
    )

    score = _clamp(score)
    previous = _clamp(_number(previous_score))

    if score > previous + 5:
        trend = "INCREASING"
    elif score < previous - 5:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    explanation = [
        f"severity_factor={severity_factor:.1f}",
        f"confidence_factor={confidence_factor:.1f}",
        f"evidence_factor={evidence_factor:.1f}",
        f"alert_factor={alert_factor:.1f}",
        f"critical_alert_factor={critical_factor:.1f}",
        f"trend={trend}",
    ]

    return RiskAnalytics(
        risk_score=score,
        severity_factor=severity_factor,
        confidence_factor=confidence_factor,
        evidence_factor=evidence_factor,
        alert_factor=alert_factor,
        trend=trend,
        explanation=explanation,
        mode="READ_ONLY",
        execution_allowed=False,
    )


def compare_risk_scores(
    current: float,
    previous: float,
) -> Dict[str, Any]:
    current_value = _clamp(_number(current))
    previous_value = _clamp(_number(previous))
    delta = current_value - previous_value

    if delta > 5:
        trend = "INCREASING"
    elif delta < -5:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    return {
        "current": current_value,
        "previous": previous_value,
        "delta": delta,
        "trend": trend,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def build_risk_report(
    analytics: RiskAnalytics,
) -> Dict[str, Any]:
    return {
        "phase": 44,
        "component": "ADVANCED_RISK_ANALYTICS",
        "risk_score": analytics.risk_score,
        "severity_factor": analytics.severity_factor,
        "confidence_factor": analytics.confidence_factor,
        "evidence_factor": analytics.evidence_factor,
        "alert_factor": analytics.alert_factor,
        "trend": analytics.trend,
        "explanation": list(analytics.explanation),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def aggregate_risk_history(
    scores: Iterable[float],
) -> Dict[str, Any]:
    values = [_clamp(_number(value)) for value in scores]

    if not values:
        return {
            "count": 0,
            "minimum": 0.0,
            "maximum": 0.0,
            "average": 0.0,
            "trend": "STABLE",
            "mode": "READ_ONLY",
            "execution_allowed": False,
        }

    average = sum(values) / len(values)

    trend = "STABLE"
    if len(values) >= 2:
        if values[-1] > values[0] + 5:
            trend = "INCREASING"
        elif values[-1] < values[0] - 5:
            trend = "DECREASING"

    return {
        "count": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "average": average,
        "trend": trend,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
