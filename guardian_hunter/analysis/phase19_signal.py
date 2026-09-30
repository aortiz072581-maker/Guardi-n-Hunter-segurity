"""Phase 19 — Defensive Signal Analysis Engine.

Observation and analysis only.
No network, process, firewall, routing or system mutation.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SignalAnalysis:
    signal_id: str
    category: str
    severity: str
    score: float
    indicators: List[str]
    confidence: float
    status: str
    mode: str
    execution_allowed: bool


def _severity(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def analyze_signal(
    signal_id: str,
    category: str,
    score: float,
    indicators: List[str],
    confidence: float = 1.0,
) -> SignalAnalysis:

    bounded_score = max(0.0, min(100.0, float(score)))
    bounded_confidence = max(0.0, min(1.0, float(confidence)))

    return SignalAnalysis(
        signal_id=str(signal_id),
        category=str(category),
        severity=_severity(bounded_score),
        score=bounded_score,
        indicators=[str(x) for x in indicators],
        confidence=bounded_confidence,
        status="OBSERVATION_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def signal_to_dict(signal: SignalAnalysis) -> Dict[str, Any]:
    return asdict(signal)


def validate_signal(signal: SignalAnalysis) -> bool:
    return (
        isinstance(signal, SignalAnalysis)
        and 0 <= signal.score <= 100
        and 0 <= signal.confidence <= 1
        and bool(signal.signal_id)
        and bool(signal.category)
        and signal.mode == "READ_ONLY"
        and signal.execution_allowed is False
        and signal.status == "OBSERVATION_ONLY"
    )
