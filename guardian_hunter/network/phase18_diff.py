"""Guardian Hunter — Phase 18.2
Network Baseline Diff
READ_ONLY / DRY_RUN only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable


@dataclass(frozen=True)
class NetworkDiff:
    added: Dict[str, list]
    removed: Dict[str, list]
    changed: Dict[str, dict]
    total_changes: int
    phase: int = 18
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


_FIELDS = (
    "interfaces",
    "addresses",
    "mac_addresses",
    "gateways",
    "routes",
    "dns_servers",
    "listeners",
    "connections",
    "egress_destinations",
)


def _items(value: Any) -> set:
    if value is None:
        return set()

    if isinstance(value, dict):
        return {tuple(sorted(value.items()))}

    if isinstance(value, (list, tuple, set)):
        result = set()
        for item in value:
            if isinstance(item, dict):
                result.add(tuple(sorted(item.items())))
            else:
                result.add(str(item))
        return result

    return {str(value)}


def compare_network_baseline(
    baseline: Dict[str, Any],
    current: Dict[str, Any],
) -> NetworkDiff:
    added: Dict[str, list] = {}
    removed: Dict[str, list] = {}
    changed: Dict[str, dict] = {}

    for field in _FIELDS:
        old = _items(baseline.get(field, []))
        new = _items(current.get(field, []))

        add = sorted(new - old, key=str)
        rem = sorted(old - new, key=str)

        if add:
            added[field] = add

        if rem:
            removed[field] = rem

        if add or rem:
            changed[field] = {
                "added": add,
                "removed": rem,
            }

    total = sum(len(v) for v in added.values()) + sum(
        len(v) for v in removed.values()
    )

    return NetworkDiff(
        added=added,
        removed=removed,
        changed=changed,
        total_changes=total,
    )


def validate_network_diff(diff: NetworkDiff) -> bool:
    return (
        diff.phase == 18
        and diff.mode == "READ_ONLY"
        and diff.execution_allowed is False
        and diff.total_changes >= 0
    )


__all__ = [
    "NetworkDiff",
    "compare_network_baseline",
    "validate_network_diff",
]
