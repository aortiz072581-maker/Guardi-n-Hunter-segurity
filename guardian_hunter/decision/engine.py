"""Phase 22 — Defensive Decision Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Decision:
    decision: str
    priority: str
    risk_score: float
    confidence: float
    rationale: list[str]
    requires_approval: bool
    execution_allowed: bool
    mode: str
    timestamp: str


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def make_decision(
    finding: dict[str, Any] | None = None,
    *,
    risk_score: float | None = None,
    confidence: float = 0.0,
    context: dict[str, Any] | None = None,
    mode: str = "DRY_RUN",
) -> dict[str, Any]:
    finding = finding or {}
    context = context or {}

    score = (
        _number(risk_score)
        if risk_score is not None
        else _number(
            finding.get(
                "risk_score",
                finding.get("score", finding.get("risk", 0)),
            )
        )
    )

    confidence_value = max(0.0, min(1.0, _number(confidence)))

    rationale: list[str] = []

    if score >= 80:
        priority = "CRITICAL"
        decision = "CONTAINMENT_REVIEW"
        rationale.append("high risk score")
    elif score >= 60:
        priority = "HIGH"
        decision = "ESCALATION_REVIEW"
        rationale.append("elevated risk score")
    elif score >= 30:
        priority = "MEDIUM"
        decision = "MONITOR"
        rationale.append("moderate risk score")
    else:
        priority = "LOW"
        decision = "OBSERVE"
        rationale.append("low risk score")

    if context.get("known_asset") is False:
        rationale.append("asset is not known")

    if context.get("repeated_signal"):
        rationale.append("signal is repeated")

    if confidence_value < 0.5:
        rationale.append("confidence below review threshold")

    # Phase 22 never enables real execution by itself.
    requires_approval = decision in {
        "CONTAINMENT_REVIEW",
        "ESCALATION_REVIEW",
    }

    execution_allowed = False

    if mode != "DRY_RUN":
        # Explicitly remain blocked until a future controlled gate authorizes it.
        rationale.append("execution remains blocked by security policy")

    result = Decision(
        decision=decision,
        priority=priority,
        risk_score=score,
        confidence=confidence_value,
        rationale=rationale,
        requires_approval=requires_approval,
        execution_allowed=execution_allowed,
        mode="DRY_RUN",
        timestamp=_utc_now(),
    )

    return asdict(result)


def explain_decision(decision: dict[str, Any]) -> str:
    rationale = decision.get("rationale") or []
    if not rationale:
        return "No rationale recorded."
    return "; ".join(str(item) for item in rationale)
