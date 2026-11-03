"""Phase 26 — Intelligent defensive baseline."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def baseline_hash(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(
        _canonical(snapshot).encode("utf-8")
    ).hexdigest()


def create_baseline(
    snapshot: dict[str, Any],
    *,
    version: int = 1,
) -> dict[str, Any]:
    clean_snapshot = dict(snapshot)

    result = {
        "version": int(version),
        "created_at": _utc_now(),
        "snapshot": clean_snapshot,
    }

    result["fingerprint"] = baseline_hash(clean_snapshot)

    return result


def compare_baseline(
    baseline: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    expected = dict(baseline.get("snapshot", {}))

    changed: list[str] = []
    added: list[str] = []
    removed: list[str] = []

    for key in expected:
        if key not in current:
            removed.append(key)
        elif expected[key] != current[key]:
            changed.append(key)

    for key in current:
        if key not in expected:
            added.append(key)

    unchanged = not changed and not added and not removed

    return {
        "unchanged": unchanged,
        "changed": sorted(changed),
        "added": sorted(added),
        "removed": sorted(removed),
        "change_count": (
            len(changed) + len(added) + len(removed)
        ),
    }


def classify_changes(
    comparison: dict[str, Any],
    expected_changes: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    expected = set(expected_changes or [])

    changed_keys = set(comparison.get("changed", []))
    changed_keys.update(comparison.get("added", []))
    changed_keys.update(comparison.get("removed", []))

    expected_found = sorted(changed_keys & expected)
    unexpected = sorted(changed_keys - expected)

    if not changed_keys:
        status = "UNCHANGED"
    elif unexpected:
        status = "UNEXPECTED_CHANGE"
    else:
        status = "EXPECTED_CHANGE"

    return {
        "status": status,
        "expected_changes": expected_found,
        "unexpected_changes": unexpected,
        "change_count": len(changed_keys),
    }


def baseline_integrity(
    baseline: dict[str, Any],
) -> bool:
    snapshot = baseline.get("snapshot")

    if not isinstance(snapshot, dict):
        return False

    stored = baseline.get("fingerprint")

    if not stored:
        return False

    return baseline_hash(snapshot) == stored
