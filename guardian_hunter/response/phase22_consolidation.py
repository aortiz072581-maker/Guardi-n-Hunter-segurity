"""Phase 22 — Defensive Evidence and Timeline Consolidation."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class ConsolidatedSecurityRecord:
    event_id: str
    risk_level: str
    risk_score: float
    decision: str
    response_steps: List[str]
    evidence_ids: List[str]
    timeline_events: List[Dict[str, Any]]
    evidence_count: int
    timeline_count: int
    integrity_digest: str
    status: str
    mode: str
    execution_allowed: bool


def _canonical(data: Dict[str, Any]) -> str:
    import json
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _digest(data: Dict[str, Any]) -> str:
    return sha256(
        _canonical(data).encode("utf-8")
    ).hexdigest()


def consolidate_security_record(
    event_id: str,
    risk_level: str,
    risk_score: float,
    decision: str,
    response_steps: List[str],
    evidence_ids: List[str],
    timeline_events: List[Dict[str, Any]],
) -> ConsolidatedSecurityRecord:

    evidence_ids = [
        str(x) for x in evidence_ids
    ]

    timeline_events = list(
        timeline_events or []
    )

    payload = {
        "event_id": str(event_id),
        "risk_level": str(risk_level).upper(),
        "risk_score": float(risk_score),
        "decision": str(decision),
        "response_steps": list(response_steps),
        "evidence_ids": evidence_ids,
        "timeline_events": timeline_events,
    }

    return ConsolidatedSecurityRecord(
        event_id=str(event_id),
        risk_level=str(risk_level).upper(),
        risk_score=float(risk_score),
        decision=str(decision),
        response_steps=list(response_steps),
        evidence_ids=evidence_ids,
        timeline_events=timeline_events,
        evidence_count=len(evidence_ids),
        timeline_count=len(timeline_events),
        integrity_digest=_digest(payload),
        status="CONSOLIDATED_READ_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def consolidated_to_dict(
    record: ConsolidatedSecurityRecord,
) -> Dict[str, Any]:
    return asdict(record)


def validate_consolidated_record(
    record: ConsolidatedSecurityRecord,
) -> bool:
    return (
        isinstance(record, ConsolidatedSecurityRecord)
        and record.evidence_count
        == len(record.evidence_ids)
        and record.timeline_count
        == len(record.timeline_events)
        and 0 <= record.risk_score <= 100
        and bool(record.integrity_digest)
        and record.status == "CONSOLIDATED_READ_ONLY"
        and record.mode == "READ_ONLY"
        and record.execution_allowed is False
    )
