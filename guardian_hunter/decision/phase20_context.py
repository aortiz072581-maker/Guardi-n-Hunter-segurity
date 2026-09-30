"""Phase 20 — Contextual Defensive Risk Analysis."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class ContextualRisk:
    correlation_score: float
    asset_exposure: float
    baseline_deviation: float
    evidence_confidence: float
    contextual_score: float
    risk_level: str
    factors: List[str]
    status: str
    mode: str
    execution_allowed: bool


def _risk_level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def calculate_contextual_risk(
    correlation_score: float,
    asset_exposure: float,
    baseline_deviation: float,
    evidence_confidence: float,
) -> ContextualRisk:

    correlation_score = max(
        0.0, min(100.0, float(correlation_score))
    )
    asset_exposure = max(
        0.0, min(100.0, float(asset_exposure))
    )
    baseline_deviation = max(
        0.0, min(100.0, float(baseline_deviation))
    )
    evidence_confidence = max(
        0.0, min(100.0, float(evidence_confidence))
    )

    score = min(
        100.0,
        correlation_score * 0.35
        + asset_exposure * 0.20
        + baseline_deviation * 0.25
        + evidence_confidence * 0.20,
    )

    factors = []

    if correlation_score >= 50:
        factors.append("MULTI_SIGNAL_CORRELATION")

    if asset_exposure >= 50:
        factors.append("ASSET_EXPOSURE")

    if baseline_deviation >= 50:
        factors.append("BASELINE_DEVIATION")

    if evidence_confidence >= 70:
        factors.append("HIGH_EVIDENCE_CONFIDENCE")

    return ContextualRisk(
        correlation_score=correlation_score,
        asset_exposure=asset_exposure,
        baseline_deviation=baseline_deviation,
        evidence_confidence=evidence_confidence,
        contextual_score=score,
        risk_level=_risk_level(score),
        factors=factors,
        status="CONTEXTUAL_ANALYSIS_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def contextual_risk_to_dict(
    risk: ContextualRisk,
) -> Dict[str, Any]:
    return asdict(risk)


def validate_contextual_risk(
    risk: ContextualRisk,
) -> bool:
    return (
        isinstance(risk, ContextualRisk)
        and 0 <= risk.contextual_score <= 100
        and risk.mode == "READ_ONLY"
        and risk.execution_allowed is False
        and risk.status == "CONTEXTUAL_ANALYSIS_ONLY"
        and risk.risk_level in {
            "NORMAL",
            "WATCH",
            "HIGH",
            "CRITICAL",
        }
    )
