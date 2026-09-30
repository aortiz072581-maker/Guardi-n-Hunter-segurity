"""Phase 18.13 — Network Security Decision."""

from dataclasses import dataclass, asdict
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkSecurityDecision:
    risk_score: float
    risk_level: str
    recommended_action: str
    evidence_required: bool
    escalation_required: bool
    decision_status: str
    phase: str = "18.13"
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _score(value: Any) -> float:
    try:
        return max(0.0, min(float(value), 100.0))
    except (TypeError, ValueError):
        return 0.0


def _level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def build_network_security_decision(
    risk_score: Any = 0,
) -> NetworkSecurityDecision:

    score = _score(risk_score)
    level = _level(score)

    if level == "CRITICAL":
        action = "ESCALATE_AND_COLLECT_EVIDENCE"
        evidence = True
        escalation = True
    elif level == "HIGH":
        action = "MONITOR_AND_COLLECT_EVIDENCE"
        evidence = True
        escalation = True
    elif level == "WATCH":
        action = "ENHANCED_MONITORING"
        evidence = True
        escalation = False
    else:
        action = "CONTINUE_MONITORING"
        evidence = False
        escalation = False

    return NetworkSecurityDecision(
        risk_score=score,
        risk_level=level,
        recommended_action=action,
        evidence_required=evidence,
        escalation_required=escalation,
        decision_status="DEFENSIVE_DECISION_ONLY",
    )


def decision_to_dict(
    decision: NetworkSecurityDecision,
) -> Dict[str, Any]:
    return asdict(decision)


def validate_network_security_decision(
    decision: NetworkSecurityDecision,
) -> bool:

    return (
        isinstance(decision, NetworkSecurityDecision)
        and 0 <= decision.risk_score <= 100
        and decision.risk_level in {
            "NORMAL",
            "WATCH",
            "HIGH",
            "CRITICAL",
        }
        and decision.decision_status
        == "DEFENSIVE_DECISION_ONLY"
        and decision.phase == "18.13"
        and decision.mode == "READ_ONLY"
        and decision.execution_allowed is False
    )
