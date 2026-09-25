"""Phase 41 — Defensive Incident Intelligence.

Provides explainable context and prioritization.
It does not execute response actions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class IncidentContext:
    incident_id: str
    asset: str
    category: str
    severity: str
    risk_score: float
    confidence: float
    evidence_count: int
    related_alerts: int
    priority: str
    mode: str
    execution_allowed: bool


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_priority(
    risk_score: float,
    confidence: float,
    evidence_count: int,
    related_alerts: int,
) -> str:
    """Explainable priority calculation; no automated response."""
    risk = _number(risk_score)
    confidence = max(0.0, min(100.0, _number(confidence)))

    evidence_factor = min(int(evidence_count), 10) * 2
    alert_factor = min(int(related_alerts), 10) * 2

    score = (risk * 0.65) + (confidence * 0.25)
    score += evidence_factor + alert_factor

    if score >= 80:
        return "P1"
    if score >= 60:
        return "P2"
    if score >= 30:
        return "P3"
    return "P4"


def build_incident_context(
    *,
    incident_id: str,
    asset: str = "unknown",
    category: str = "unknown",
    severity: str = "UNKNOWN",
    risk_score: float = 0.0,
    confidence: float = 0.0,
    evidence_count: int = 0,
    related_alerts: int = 0,
) -> IncidentContext:
    priority = calculate_priority(
        risk_score,
        confidence,
        evidence_count,
        related_alerts,
    )

    return IncidentContext(
        incident_id=str(incident_id),
        asset=str(asset),
        category=str(category),
        severity=str(severity),
        risk_score=max(0.0, min(100.0, _number(risk_score))),
        confidence=max(0.0, min(100.0, _number(confidence))),
        evidence_count=max(0, int(evidence_count)),
        related_alerts=max(0, int(related_alerts)),
        priority=priority,
        mode="READ_ONLY",
        execution_allowed=False,
    )


def build_investigation_timeline(
    events: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a deterministic, non-mutating investigation timeline."""
    normalized = []

    for index, event in enumerate(events):
        item = dict(event)
        item["_sequence"] = index
        normalized.append(item)

    normalized.sort(
        key=lambda item: (
            str(item.get("timestamp", "")),
            int(item.get("_sequence", 0)),
        )
    )

    result = []
    for item in normalized:
        item.pop("_sequence", None)
        result.append(item)

    return result


def build_investigation_report(
    context: IncidentContext,
    timeline: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "phase": 41,
        "component": "INCIDENT_INTELLIGENCE",
        "incident_id": context.incident_id,
        "asset": context.asset,
        "category": context.category,
        "severity": context.severity,
        "risk_score": context.risk_score,
        "confidence": context.confidence,
        "evidence_count": context.evidence_count,
        "related_alerts": context.related_alerts,
        "priority": context.priority,
        "timeline": list(timeline),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
