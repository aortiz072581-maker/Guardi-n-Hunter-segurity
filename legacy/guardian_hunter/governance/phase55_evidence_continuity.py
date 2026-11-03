"""Phase 55 — Defensive Evidence Continuity."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class EvidenceContinuity:
    evidence_count: int
    evidence_integrity: bool
    chain_integrity: bool
    evidence_preserved: bool
    continuity_valid: bool
    execution_blocked: bool
    digest: str = ""


def _canonical(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _digest(data):
    clean = dict(data)
    clean.pop("digest", None)
    return sha256(_canonical(clean).encode()).hexdigest()


def build_evidence_continuity(
    evidence_count=0,
    evidence_integrity=True,
    chain_integrity=True,
):
    evidence_count = max(0, int(evidence_count))

    evidence_preserved = (
        evidence_integrity
        and chain_integrity
        and READ_ONLY
        and DRY_RUN
    )

    continuity_valid = evidence_preserved

    payload = EvidenceContinuity(
        evidence_count=evidence_count,
        evidence_integrity=evidence_integrity,
        chain_integrity=chain_integrity,
        evidence_preserved=evidence_preserved,
        continuity_valid=continuity_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return EvidenceContinuity(**data)


def evidence_continuity_to_dict(record):
    return asdict(record)


def validate_evidence_continuity(record):
    if not isinstance(record, EvidenceContinuity):
        return False

    data = asdict(record)

    if record.evidence_count < 0:
        return False

    if record.execution_blocked is not True:
        return False

    if record.continuity_valid is not True:
        return False

    return record.digest == _digest(data)
