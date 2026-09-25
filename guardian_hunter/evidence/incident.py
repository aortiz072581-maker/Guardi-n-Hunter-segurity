"""Phase 24 — Evidence-backed incident timeline."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def evidence_hash(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_incident_record(
    *,
    incident_id: str,
    decision: dict[str, Any] | None = None,
    correlation: dict[str, Any] | None = None,
    timeline: list[dict[str, Any]] | None = None,
    evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    decision = decision or {}
    correlation = correlation or {}
    timeline = list(timeline or [])
    evidence = list(evidence or [])

    record = {
        "incident_id": incident_id,
        "created_at": _utc_now(),
        "decision": decision,
        "correlation": correlation,
        "timeline": timeline,
        "evidence": evidence,
    }

    record["evidence_hash"] = evidence_hash(record)

    return record


def verify_incident_record(record: dict[str, Any]) -> bool:
    if not isinstance(record, dict):
        return False

    stored_hash = record.get("evidence_hash")

    if not stored_hash:
        return False

    copy = dict(record)
    copy.pop("evidence_hash", None)

    return evidence_hash(copy) == stored_hash


def append_evidence(
    evidence: list[dict[str, Any]] | None,
    item: dict[str, Any],
) -> list[dict[str, Any]]:
    result = list(evidence or [])

    entry = dict(item)
    entry.setdefault("captured_at", _utc_now())
    entry["hash"] = evidence_hash(
        {key: value for key, value in entry.items() if key != "hash"}
    )

    result.append(entry)

    return result
