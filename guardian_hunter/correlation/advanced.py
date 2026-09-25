"""Phase 23 — Advanced defensive event correlation."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any


def _value(event: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in event and event[key] is not None:
            return event[key]
    return default


def _timestamp(event: dict[str, Any]) -> str:
    return str(_value(event, "timestamp", "time", "created_at", default=""))


def correlate_events(
    events: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    events = list(events or [])

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for event in events:
        asset = str(
            _value(
                event,
                "asset_id",
                "asset",
                "host",
                "hostname",
                default="unknown",
            )
        )

        category = str(
            _value(
                event,
                "category",
                "type",
                "signal",
                "kind",
                default="unknown",
            )
        )

        key = f"{asset}:{category}"
        groups[key].append(dict(event))

    incidents = []

    for key, grouped in groups.items():
        ordered = sorted(grouped, key=_timestamp)

        incidents.append(
            {
                "correlation_key": key,
                "event_count": len(ordered),
                "first_seen": _timestamp(ordered[0]) if ordered else "",
                "last_seen": _timestamp(ordered[-1]) if ordered else "",
                "events": ordered,
            }
        )

    incidents.sort(
        key=lambda item: (
            item.get("first_seen", ""),
            item.get("correlation_key", ""),
        )
    )

    return {
        "event_count": len(events),
        "incident_count": len(incidents),
        "incidents": incidents,
    }


def build_timeline(
    events: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    events = list(events or [])

    timeline = []

    for index, event in enumerate(events, start=1):
        timestamp = _timestamp(event)

        timeline.append(
            {
                "sequence": index,
                "timestamp": timestamp,
                "type": _value(
                    event,
                    "type",
                    "category",
                    "signal",
                    "kind",
                    default="event",
                ),
                "asset": _value(
                    event,
                    "asset_id",
                    "asset",
                    "host",
                    "hostname",
                    default="unknown",
                ),
                "summary": _value(
                    event,
                    "summary",
                    "message",
                    "description",
                    default="",
                ),
            }
        )

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        timestamp = item["timestamp"]

        try:
            parsed = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )
            return (0, parsed.isoformat())
        except (ValueError, TypeError):
            return (1, str(timestamp))

    timeline.sort(key=sort_key)

    for index, item in enumerate(timeline, start=1):
        item["sequence"] = index

    return timeline
