"""Defensive diagnosis engine.

Analysis and recommendations only.
No network, process, firewall, routing, package, or system mutation.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class ProblemDiagnosis:
    categories: List[str]
    risk_level: str
    risk_score: float
    problem_detected: bool
    probable_causes: List[str]
    recommendations: List[str]
    confidence: float
    requires_human_review: bool
    status: str
    mode: str
    dry_run: bool
    execution_allowed: bool


def _risk_level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def diagnose_problem(
    correlation: Dict[str, Any],
) -> ProblemDiagnosis:

    score = max(
        0.0,
        min(
            100.0,
            float(correlation.get("correlated_score", 0.0)),
        ),
    )

    categories = sorted(
        {
            str(x).lower()
            for x in correlation.get("categories", [])
            if str(x).strip()
        }
    )

    level = _risk_level(score)
    detected = score >= 25.0

    causes: List[str] = []
    recommendations: List[str] = []

    if "network" in categories:
        causes.append("NETWORK_STATE_OR_CONNECTIVITY_CHANGE")
        recommendations.append("REVIEW_NETWORK_BASELINE_AND_RECENT_CHANGES")

    if "hardware" in categories:
        causes.append("HARDWARE_INVENTORY_OR_STATE_CHANGE")
        recommendations.append("VERIFY_HARDWARE_INVENTORY_AND_DEVICE_STATE")

    if "dns" in categories:
        causes.append("DNS_CONFIGURATION_OR_RESOLUTION_CHANGE")
        recommendations.append("REVIEW_DNS_CONFIGURATION_AND_RESOLUTION_EVIDENCE")

    if "tls" in categories:
        causes.append("TLS_CONFIGURATION_OR_CERTIFICATE_CHANGE")
        recommendations.append("REVIEW_TLS_CONFIGURATION_AND_CERTIFICATE_STATE")

    if "integrity" in categories:
        causes.append("PROTECTED_FILE_INTEGRITY_CHANGE")
        recommendations.append("REVIEW_PROTECTED_FILE_CHANGES")
        recommendations.append("VERIFY_CHANGE_AUTHORIZATION")

    if detected and not causes:
        causes.append("CORRELATED_ANOMALY_REQUIRES_FURTHER_ANALYSIS")
        recommendations.append("COLLECT_ADDITIONAL_READ_ONLY_EVIDENCE")

    if level in {"HIGH", "CRITICAL"}:
        recommendations.append("INCREASE_DEFENSIVE_MONITORING")

    if level == "CRITICAL":
        recommendations.append("ESCALATE_FOR_HUMAN_REVIEW")

    recommendations.append("KEEP_RESPONSE_LOCKED")

    # Conservative confidence: correlation strength expressed as 0..1.
    confidence = round(score / 100.0, 4)

    return ProblemDiagnosis(
        categories=categories,
        risk_level=level,
        risk_score=score,
        problem_detected=detected,
        probable_causes=causes,
        recommendations=recommendations,
        confidence=confidence,
        requires_human_review=(level == "CRITICAL"),
        status="DIAGNOSIS_ONLY",
        mode="READ_ONLY",
        dry_run=True,
        execution_allowed=False,
    )


def diagnosis_to_dict(
    diagnosis: ProblemDiagnosis,
) -> Dict[str, Any]:
    return asdict(diagnosis)


def validate_diagnosis(
    diagnosis: ProblemDiagnosis,
) -> bool:
    return (
        isinstance(diagnosis, ProblemDiagnosis)
        and 0 <= diagnosis.risk_score <= 100
        and 0 <= diagnosis.confidence <= 1
        and diagnosis.risk_level
        in {"NORMAL", "WATCH", "HIGH", "CRITICAL"}
        and diagnosis.mode == "READ_ONLY"
        and diagnosis.dry_run is True
        and diagnosis.execution_allowed is False
        and diagnosis.status == "DIAGNOSIS_ONLY"
        and "KEEP_RESPONSE_LOCKED"
        in diagnosis.recommendations
    )
