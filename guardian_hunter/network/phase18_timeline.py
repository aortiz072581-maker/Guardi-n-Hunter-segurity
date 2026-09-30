"""Phase 18.8 — Network Timeline
Deterministic observation-only timeline.
No network access, no system changes, no execution.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
PHASE = 18.8


_SEVERITY_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFO": 4,
}


@dataclass(frozen=True)
class NetworkTimelineEvent:
    event_id: str
    timestamp: Optional[str]
    event_type: str
    source: str
    severity: str
    description: str
    phase: float = PHASE
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def _safe_timestamp(value: Any) -> Optional[str]:
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def _event(
    index: int,
    event_type: str,
    source: str,
    severity: str,
    description: str,
    timestamp: Any = None,
) -> NetworkTimelineEvent:

    severity = str(severity).upper()

    if severity not in _SEVERITY_ORDER:
        severity = "INFO"

    return NetworkTimelineEvent(
        event_id=f"NET18-{index:04d}",
        timestamp=_safe_timestamp(timestamp),
        event_type=str(event_type),
        source=str(source),
        severity=severity,
        description=str(description),
    )


def build_network_timeline(
    *,
    diff: Optional[Any] = None,
    anomalies: Optional[Sequence[Any]] = None,
    dns: Optional[Any] = None,
    listeners: Optional[Any] = None,
    connections: Optional[Any] = None,
) -> List[NetworkTimelineEvent]:

    events: List[NetworkTimelineEvent] = []
    index = 1

    # ----------------------------------------------
    # BASELINE DIFF — PHASE 18.2
    # ----------------------------------------------

    if diff is not None:
        added = getattr(diff, "added", {}) or {}
        removed = getattr(diff, "removed", {}) or {}
        changed = getattr(diff, "changed", {}) or {}

        for category, values in sorted(added.items()):
            for value in values:
                events.append(
                    _event(
                        index,
                        "BASELINE_ADDED",
                        "18.2",
                        "MEDIUM",
                        f"{category}: added {value}",
                    )
                )
                index += 1

        for category, values in sorted(removed.items()):
            for value in values:
                events.append(
                    _event(
                        index,
                        "BASELINE_REMOVED",
                        "18.2",
                        "MEDIUM",
                        f"{category}: removed {value}",
                    )
                )
                index += 1

        for category, values in sorted(changed.items()):
            for value in values:
                events.append(
                    _event(
                        index,
                        "BASELINE_CHANGED",
                        "18.2",
                        "HIGH",
                        f"{category}: changed {value}",
                    )
                )
                index += 1

    # ----------------------------------------------
    # ANOMALIES — PHASE 18.3
    # ----------------------------------------------

    if anomalies:
        for anomaly in anomalies:

            category = getattr(
                anomaly,
                "category",
                "network",
            )

            severity = getattr(
                anomaly,
                "severity",
                "LOW",
            )

            description = getattr(
                anomaly,
                "description",
                str(anomaly),
            )

            timestamp = getattr(
                anomaly,
                "timestamp",
                None,
            )

            events.append(
                _event(
                    index,
                    "ANOMALY",
                    "18.3",
                    severity,
                    f"{category}: {description}",
                    timestamp,
                )
            )

            index += 1

    # ----------------------------------------------
    # DNS — PHASE 18.5
    # ----------------------------------------------

    if dns is not None:
        for item in getattr(
            dns,
            "observations",
            [],
        ) or []:

            status = item.get(
                "status",
                "OBSERVED",
            )

            severity = (
                "HIGH"
                if status == "NEW"
                else "MEDIUM"
            )

            events.append(
                _event(
                    index,
                    "DNS_OBSERVATION",
                    "18.5",
                    severity,
                    str(item),
                    item.get("timestamp"),
                )
            )

            index += 1

    # ----------------------------------------------
    # LISTENERS — PHASE 18.6
    # ----------------------------------------------

    if listeners is not None:
        for item in getattr(
            listeners,
            "observations",
            [],
        ) or []:

            severity = item.get(
                "severity",
                "LOW",
            )

            events.append(
                _event(
                    index,
                    "LISTENER_OBSERVATION",
                    "18.6",
                    severity,
                    str(item),
                    item.get("timestamp"),
                )
            )

            index += 1

    # ----------------------------------------------
    # CONNECTION / EGRESS — PHASE 18.7
    # ----------------------------------------------

    if connections is not None:
        for item in getattr(
            connections,
            "observations",
            [],
        ) or []:

            severity = item.get(
                "severity",
                "LOW",
            )

            events.append(
                _event(
                    index,
                    "CONNECTION_OBSERVATION",
                    "18.7",
                    severity,
                    str(item),
                    item.get("timestamp"),
                )
            )

            index += 1

    # ----------------------------------------------
    # DETERMINISTIC ORDER
    # ----------------------------------------------

    events.sort(
        key=lambda item: (
            item.timestamp is None,
            item.timestamp or "",
            item.source,
            _SEVERITY_ORDER.get(
                item.severity,
                99,
            ),
            item.event_id,
        )
    )

    return events


def timeline_to_dict(
    timeline: Sequence[NetworkTimelineEvent],
) -> List[Dict[str, Any]]:

    return [
        asdict(event)
        for event in timeline
    ]


def build_timeline_summary(
    timeline: Sequence[NetworkTimelineEvent],
) -> Dict[str, Any]:

    severity_counts: Dict[str, int] = {}

    source_counts: Dict[str, int] = {}

    event_type_counts: Dict[str, int] = {}

    for event in timeline:

        severity_counts[event.severity] = (
            severity_counts.get(
                event.severity,
                0,
            ) + 1
        )

        source_counts[event.source] = (
            source_counts.get(
                event.source,
                0,
            ) + 1
        )

        event_type_counts[event.event_type] = (
            event_type_counts.get(
                event.event_type,
                0,
            ) + 1
        )

    return {
        "phase": PHASE,
        "total_events": len(timeline),
        "severity_counts": dict(
            sorted(severity_counts.items())
        ),
        "source_counts": dict(
            sorted(source_counts.items())
        ),
        "event_type_counts": dict(
            sorted(event_type_counts.items())
        ),
        "read_only": True,
        "dry_run": True,
        "execution_allowed": False,
    }


def validate_network_timeline(
    timeline: Sequence[NetworkTimelineEvent],
) -> bool:

    if not isinstance(timeline, list):
        return False

    previous_key = None

    for event in timeline:

        if not isinstance(
            event,
            NetworkTimelineEvent,
        ):
            return False

        if event.phase != PHASE:
            return False

        if event.mode != "READ_ONLY":
            return False

        if event.execution_allowed is not False:
            return False

        if event.severity not in _SEVERITY_ORDER:
            return False

        current_key = (
            event.timestamp is None,
            event.timestamp or "",
            event.source,
            _SEVERITY_ORDER.get(
                event.severity,
                99,
            ),
            event.event_id,
        )

        if (
            previous_key is not None
            and current_key < previous_key
        ):
            return False

        previous_key = current_key

    return True
