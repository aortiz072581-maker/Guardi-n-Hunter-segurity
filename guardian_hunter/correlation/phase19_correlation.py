"""Phase 19 — Multi-Signal Correlation."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SignalCorrelation:
    signal_ids: List[str]
    categories: List[str]
    signal_count: int
    average_score: float
    maximum_score: float
    correlated_score: float
    correlation_level: str
    status: str
    mode: str
    execution_allowed: bool


def _level(score: float) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "WATCH"
    return "NORMAL"


def correlate_signals(
    signals: List[Dict[str, Any]],
) -> SignalCorrelation:

    items = list(signals or [])

    scores = [
        max(0.0, min(100.0, float(item.get("score", 0))))
        for item in items
    ]

    signal_ids = [
        str(item.get("signal_id", "UNKNOWN"))
        for item in items
    ]

    categories = sorted(
        {
            str(item.get("category", "unknown"))
            for item in items
        }
    )

    if scores:
        average = sum(scores) / len(scores)
        maximum = max(scores)

        # Conservative correlation:
        # average contributes 40%, maximum contributes 60%.
        correlated = min(
            100.0,
            (average * 0.40) + (maximum * 0.60),
        )
    else:
        average = 0.0
        maximum = 0.0
        correlated = 0.0

    return SignalCorrelation(
        signal_ids=signal_ids,
        categories=categories,
        signal_count=len(items),
        average_score=average,
        maximum_score=maximum,
        correlated_score=correlated,
        correlation_level=_level(correlated),
        status="CORRELATION_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def correlation_to_dict(
    correlation: SignalCorrelation,
) -> Dict[str, Any]:
    return asdict(correlation)


def validate_signal_correlation(
    correlation: SignalCorrelation,
) -> bool:
    return (
        isinstance(correlation, SignalCorrelation)
        and correlation.signal_count == len(correlation.signal_ids)
        and 0 <= correlation.average_score <= 100
        and 0 <= correlation.maximum_score <= 100
        and 0 <= correlation.correlated_score <= 100
        and correlation.mode == "READ_ONLY"
        and correlation.execution_allowed is False
        and correlation.status == "CORRELATION_ONLY"
    )
