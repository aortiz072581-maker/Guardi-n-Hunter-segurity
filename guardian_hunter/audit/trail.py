"""Phase 31 — Tamper-evident defensive audit trail."""

from datetime import datetime, timezone
import hashlib
import json


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def event_hash(event):
    payload = dict(event)
    payload.pop("hash", None)
    return hashlib.sha256(
        _canonical(payload).encode("utf-8")
    ).hexdigest()


def create_event(
    *,
    event_type,
    source,
    severity="INFO",
    details=None,
    previous_hash=None,
):
    event = {
        "timestamp": _utc_now(),
        "event_type": str(event_type),
        "source": str(source),
        "severity": str(severity),
        "details": details or {},
        "previous_hash": previous_hash,
    }

    event["hash"] = event_hash(event)
    return event


def append_event(trail, event):
    """Append only a validated audit event."""
    if not isinstance(trail, list):
        raise TypeError("trail must be a list")

    if event_hash(event) != event.get("hash"):
        raise ValueError("invalid event hash")

    if trail:
        expected_previous = trail[-1].get("hash")
        if event.get("previous_hash") != expected_previous:
            raise ValueError("audit chain mismatch")

    trail.append(dict(event))
    return trail


def verify_trail(trail):
    """Verify hashes and chain continuity."""
    previous = None

    for event in trail:
        if event_hash(event) != event.get("hash"):
            return {
                "valid": False,
                "reason": "HASH_MISMATCH",
            }

        if event.get("previous_hash") != previous:
            return {
                "valid": False,
                "reason": "CHAIN_MISMATCH",
            }

        previous = event.get("hash")

    return {
        "valid": True,
        "events": len(trail),
        "last_hash": previous,
    }
