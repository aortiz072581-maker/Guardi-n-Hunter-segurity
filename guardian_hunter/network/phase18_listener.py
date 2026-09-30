"""Phase 18.6 — Listener Intelligence
Observation-only listener analysis.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
PHASE = 18.6


def _normalize_listener(value: Any) -> str:
    if isinstance(value, dict):
        protocol = value.get("protocol", "")
        address = value.get("address") or value.get("host") or ""
        port = value.get("port", "")

        return ":".join(
            part for part in (
                str(protocol).strip().lower(),
                str(address).strip().lower(),
                str(port).strip(),
            )
            if part != ""
        )

    return str(value).strip().lower()


def _listener_items(values: Optional[Sequence[Any]]) -> List[str]:
    if not values:
        return []

    result = []

    for value in values:
        item = _normalize_listener(value)
        if item and item not in result:
            result.append(item)

    return sorted(result)


@dataclass(frozen=True)
class ListenerIntelligence:
    baseline_listeners: List[str]
    current_listeners: List[str]
    new_listeners: List[str]
    removed_listeners: List[str]
    known_listeners: List[str]
    changed: bool
    risk_count: int
    observations: List[Dict[str, Any]]
    phase: float = PHASE
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def analyze_listener_intelligence(
    baseline_listeners: Optional[Sequence[Any]] = None,
    current_listeners: Optional[Sequence[Any]] = None,
) -> ListenerIntelligence:

    baseline = _listener_items(baseline_listeners)
    current = _listener_items(current_listeners)

    new = sorted(set(current) - set(baseline))
    removed = sorted(set(baseline) - set(current))
    known = sorted(set(current) & set(baseline))

    observations: List[Dict[str, Any]] = []

    for listener in new:
        observations.append(
            {
                "listener": listener,
                "status": "NEW_LISTENER",
                "severity": "HIGH",
                "read_only": True,
            }
        )

    for listener in known:
        observations.append(
            {
                "listener": listener,
                "status": "KNOWN_LISTENER",
                "severity": "LOW",
                "read_only": True,
            }
        )

    for listener in removed:
        observations.append(
            {
                "listener": listener,
                "status": "REMOVED_LISTENER",
                "severity": "MEDIUM",
                "read_only": True,
            }
        )

    return ListenerIntelligence(
        baseline_listeners=baseline,
        current_listeners=current,
        new_listeners=new,
        removed_listeners=removed,
        known_listeners=known,
        changed=bool(new or removed),
        risk_count=len(new),
        observations=observations,
    )


def listener_intelligence_to_dict(
    result: ListenerIntelligence,
) -> Dict[str, Any]:
    return asdict(result)


def validate_listener_intelligence(
    result: ListenerIntelligence,
) -> bool:
    return (
        isinstance(result, ListenerIntelligence)
        and result.phase == PHASE
        and result.mode == "READ_ONLY"
        and result.execution_allowed is False
        and isinstance(result.baseline_listeners, list)
        and isinstance(result.current_listeners, list)
        and isinstance(result.new_listeners, list)
        and isinstance(result.removed_listeners, list)
        and isinstance(result.known_listeners, list)
        and isinstance(result.observations, list)
        and result.risk_count == len(result.new_listeners)
        and result.changed
        == bool(result.new_listeners or result.removed_listeners)
    )
