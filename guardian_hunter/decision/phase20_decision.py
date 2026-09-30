"""Phase 20 — Defensive Decision Engine.

Produces recommendations for review only.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class DefensiveDecision:
    risk_level: str
    risk_score: float
    decision: str
    requires_review: bool
    collect_evidence: bool
    response_locked: bool
    status: str
    mode: str
    execution_allowed: bool


def build_defensive_decision(
    risk_level: str,
    risk_score: float,
) -> DefensiveDecision:

    level = str(risk_level).upper()
    score = max(0.0, min(100.0, float(risk_score)))

    if level == "CRITICAL":
        decision = "ESCALATE_FOR_HUMAN_REVIEW"
        review = True
        evidence = True

    elif level == "HIGH":
        decision = "ENHANCED_MONITORING_AND_REVIEW"
        review = True
        evidence = True

    elif level == "WATCH":
        decision = "ENHANCED_MONITORING"
        review = False
        evidence = True

    else:
        decision = "CONTINUE_MONITORING"
        review = False
        evidence = False

    return DefensiveDecision(
        risk_level=level,
        risk_score=score,
        decision=decision,
        requires_review=review,
        collect_evidence=evidence,
        response_locked=True,
        status="DEFENSIVE_DECISION_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def decision_to_dict(
    decision: DefensiveDecision,
) -> Dict[str, Any]:
    return asdict(decision)


def validate_defensive_decision(
    decision: DefensiveDecision,
) -> bool:
    return (
        isinstance(decision, DefensiveDecision)
        and 0 <= decision.risk_score <= 100
        and decision.response_locked is True
        and decision.mode == "READ_ONLY"
        and decision.execution_allowed is False
        and decision.status == "DEFENSIVE_DECISION_ONLY"
    )
