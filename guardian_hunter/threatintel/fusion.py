"""Phase 37 — Defensive Threat Intelligence Fusion."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


VALID_TYPES = (
    "IP",
    "DOMAIN",
    "URL",
    "HASH",
    "EMAIL",
    "UNKNOWN",
)


@dataclass(frozen=True)
class Indicator:
    value: str
    indicator_type: str
    source: str = "local"
    confidence: float = 0.0
    severity: str = "INFO"


def normalize_indicator(
    value: str,
    indicator_type: str = "UNKNOWN",
    source: str = "local",
    confidence: float = 0.0,
    severity: str = "INFO",
) -> Indicator:
    clean_value = str(value).strip().lower()

    if not clean_value:
        raise ValueError("indicator value required")

    normalized_type = str(indicator_type).upper()

    if normalized_type not in VALID_TYPES:
        normalized_type = "UNKNOWN"

    confidence = max(0.0, min(100.0, float(confidence)))

    return Indicator(
        value=clean_value,
        indicator_type=normalized_type,
        source=str(source),
        confidence=confidence,
        severity=str(severity).upper(),
    )


def fuse_indicators(indicators: list[Indicator]) -> dict[str, Any]:
    unique: dict[tuple[str, str], Indicator] = {}

    for indicator in indicators:
        key = (indicator.indicator_type, indicator.value)

        current = unique.get(key)

        if current is None or indicator.confidence > current.confidence:
            unique[key] = indicator

    records = [
        {
            "value": item.value,
            "type": item.indicator_type,
            "source": item.source,
            "confidence": item.confidence,
            "severity": item.severity,
        }
        for item in unique.values()
    ]

    return {
        "timestamp": _utc_now(),
        "indicator_count": len(records),
        "indicators": records,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def correlate_indicator(
    indicator: Indicator,
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    matches = []

    for event in events:
        text = str(event).lower()

        if indicator.value in text:
            matches.append(event)

    return matches
