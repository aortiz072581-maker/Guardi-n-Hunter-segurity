"""Phase 18.10 — Network Risk Scoring."""

from dataclasses import dataclass, asdict
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkRiskAssessment:
    baseline_anomaly_score: float
    dns_score: float
    listener_score: float
    connection_score: float
    correlation_score: float
    total_score: float
    risk_level: str
    phase: str = "18.10"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _number(value: Any) -> float:
    try:
        return max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return 0.0


def _risk_level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def calculate_network_risk(
    baseline_anomaly_score: Any = 0,
    dns_score: Any = 0,
    listener_score: Any = 0,
    connection_score: Any = 0,
    correlation_score: Any = 0,
) -> NetworkRiskAssessment:

    scores = {
        "baseline_anomaly_score": _number(
            baseline_anomaly_score
        ),
        "dns_score": _number(dns_score),
        "listener_score": _number(listener_score),
        "connection_score": _number(connection_score),
        "correlation_score": _number(correlation_score),
    }

    total = (
        scores["baseline_anomaly_score"] * 0.30
        + scores["dns_score"] * 0.15
        + scores["listener_score"] * 0.20
        + scores["connection_score"] * 0.20
        + scores["correlation_score"] * 0.15
    )

    total = round(min(total, 100.0), 2)

    return NetworkRiskAssessment(
        **scores,
        total_score=total,
        risk_level=_risk_level(total),
    )


def risk_to_dict(
    assessment: NetworkRiskAssessment,
) -> Dict[str, Any]:
    return asdict(assessment)


def validate_network_risk(
    assessment: NetworkRiskAssessment,
) -> bool:

    return (
        isinstance(assessment, NetworkRiskAssessment)
        and 0 <= assessment.total_score <= 100
        and assessment.risk_level in {
            "NORMAL",
            "WATCH",
            "HIGH",
            "CRITICAL",
        }
        and assessment.phase == "18.10"
        and assessment.mode == "READ_ONLY"
        and assessment.execution_allowed is False
    )
