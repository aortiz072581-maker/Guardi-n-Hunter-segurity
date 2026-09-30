"""
Guardian Hunter — Evidence Persistence & Integrity v1

Defensive evidence persistence.

The store:
- persists evidence as append-only JSONL,
- calculates SHA-256 hashes,
- chains records together,
- detects modification,
- detects chain breaks,
- survives a new store instance,
- never executes response actions.

Safety invariants are hard-coded fail-closed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True

GENESIS = "0" * 64


@dataclass(frozen=True)
class EvidenceRecord:
    sequence: int
    evidence_id: str
    event_type: str
    timestamp: float
    payload: Mapping[str, Any]
    previous_hash: str
    record_hash: str


@dataclass(frozen=True)
class EvidenceVerification:
    state: str
    records: int
    invalid_sequence: bool
    invalid_hash: bool
    invalid_chain: bool
    execution_allowed: bool
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool


def safety_invariants_hold() -> bool:
    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )


def _canonical(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _calculate_hash(
    sequence: int,
    evidence_id: str,
    event_type: str,
    timestamp: float,
    payload: Mapping[str, Any],
    previous_hash: str,
) -> str:
    body = {
        "sequence": sequence,
        "evidence_id": evidence_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "payload": dict(payload),
        "previous_hash": previous_hash,
    }

    return sha256(_canonical(body)).hexdigest()


def _record_to_dict(record: EvidenceRecord) -> dict[str, Any]:
    return {
        "sequence": record.sequence,
        "evidence_id": record.evidence_id,
        "event_type": record.event_type,
        "timestamp": record.timestamp,
        "payload": dict(record.payload),
        "previous_hash": record.previous_hash,
        "record_hash": record.record_hash,
    }


def _dict_to_record(data: Mapping[str, Any]) -> EvidenceRecord:
    return EvidenceRecord(
        sequence=int(data["sequence"]),
        evidence_id=str(data["evidence_id"]),
        event_type=str(data["event_type"]),
        timestamp=float(data["timestamp"]),
        payload=dict(data["payload"]),
        previous_hash=str(data["previous_hash"]),
        record_hash=str(data["record_hash"]),
    )


class EvidenceStore:
    """Append-only evidence store."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _load(self) -> list[EvidenceRecord]:
        if not self.path.exists():
            return []

        records: list[EvidenceRecord] = []

        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                records.append(
                    _dict_to_record(json.loads(line))
                )

        return records

    def append(
        self,
        *,
        evidence_id: str,
        event_type: str,
        timestamp: float,
        payload: Mapping[str, Any],
    ) -> EvidenceRecord:
        if not safety_invariants_hold():
            raise RuntimeError("SAFETY_INVARIANTS_FAILED")

        records = self._load()

        sequence = len(records) + 1

        previous_hash = (
            records[-1].record_hash
            if records
            else GENESIS
        )

        record_hash = _calculate_hash(
            sequence,
            evidence_id,
            event_type,
            timestamp,
            payload,
            previous_hash,
        )

        record = EvidenceRecord(
            sequence=sequence,
            evidence_id=evidence_id,
            event_type=event_type,
            timestamp=timestamp,
            payload=dict(payload),
            previous_hash=previous_hash,
            record_hash=record_hash,
        )

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    _record_to_dict(record),
                    sort_keys=True,
                    ensure_ascii=False,
                )
                + "\n"
            )

        return record

    def records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(self._load())

    def verify(self) -> EvidenceVerification:
        records = self._load()

        previous_hash = GENESIS

        invalid_sequence = False
        invalid_hash = False
        invalid_chain = False

        for expected_sequence, record in enumerate(
            records,
            start=1,
        ):
            if record.sequence != expected_sequence:
                invalid_sequence = True

            if record.previous_hash != previous_hash:
                invalid_chain = True

            expected_hash = _calculate_hash(
                record.sequence,
                record.evidence_id,
                record.event_type,
                record.timestamp,
                record.payload,
                record.previous_hash,
            )

            if record.record_hash != expected_hash:
                invalid_hash = True

            previous_hash = record.record_hash

        valid = not (
            invalid_sequence
            or invalid_hash
            or invalid_chain
        )

        return EvidenceVerification(
            state=(
                "EVIDENCE_INTEGRITY_OK"
                if valid
                else "EVIDENCE_TAMPER_DETECTED"
            ),
            records=len(records),
            invalid_sequence=invalid_sequence,
            invalid_hash=invalid_hash,
            invalid_chain=invalid_chain,
            execution_allowed=False,
            read_only=READ_ONLY,
            dry_run=DRY_RUN,
            real_execution_blocked=REAL_EXECUTION_BLOCKED,
            human_review_required=HUMAN_REVIEW_REQUIRED,
            response_locked=RESPONSE_LOCKED,
        )


def fail_closed(result: EvidenceVerification) -> bool:
    return (
        result.execution_allowed is False
        and result.read_only is True
        and result.dry_run is True
        and result.real_execution_blocked is True
        and result.human_review_required is True
        and result.response_locked is True
    )
