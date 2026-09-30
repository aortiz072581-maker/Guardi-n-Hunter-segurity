"""Phase 67 — Defensive Traceability."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveTraceability:
    event_count: int
    source_links_valid: bool
    decision_links_valid: bool
    evidence_links_valid: bool
    traceability_valid: bool
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


def build_traceability(
    event_count=0,
    source_links_valid=True,
    decision_links_valid=True,
    evidence_links_valid=True,
):
    event_count = max(0, int(event_count))

    traceability_valid = all(
        [
            source_links_valid,
            decision_links_valid,
            evidence_links_valid,
            READ_ONLY,
            DRY_RUN,
            not EXECUTION_ALLOWED,
        ]
    )

    payload = DefensiveTraceability(
        event_count=event_count,
        source_links_valid=source_links_valid,
        decision_links_valid=decision_links_valid,
        evidence_links_valid=evidence_links_valid,
        traceability_valid=traceability_valid,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return DefensiveTraceability(**data)


def traceability_to_dict(record):
    return asdict(record)


def validate_traceability(record):
    if not isinstance(record, DefensiveTraceability):
        return False

    data = asdict(record)

    if record.event_count < 0:
        return False

    if record.execution_blocked is not True:
        return False

    if record.traceability_valid is not True:
        return False

    return record.digest == _digest(data)
