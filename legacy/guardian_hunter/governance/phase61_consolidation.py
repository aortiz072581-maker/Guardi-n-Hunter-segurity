"""Phase 61 — Defensive Governance Consolidation."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class GovernanceConsolidation:
    controls_valid: bool
    incidents_valid: bool
    response_valid: bool
    audit_valid: bool
    governance_score: int
    governance_state: str
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


def build_governance_consolidation(
    controls_valid,
    incidents_valid,
    response_valid,
    audit_valid,
):
    checks = [
        controls_valid,
        incidents_valid,
        response_valid,
        audit_valid,
    ]

    governance_score = int((sum(checks) / 4) * 100)

    governance_state = (
        "GOVERNANCE_CONSOLIDATED"
        if all(checks)
        else "GOVERNANCE_HOLD"
    )

    payload = GovernanceConsolidation(
        controls_valid=controls_valid,
        incidents_valid=incidents_valid,
        response_valid=response_valid,
        audit_valid=audit_valid,
        governance_score=governance_score,
        governance_state=governance_state,
        execution_blocked=not EXECUTION_ALLOWED,
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return GovernanceConsolidation(**data)


def consolidation_to_dict(record):
    return asdict(record)


def validate_governance_consolidation(record):
    if not isinstance(record, GovernanceConsolidation):
        return False

    data = asdict(record)

    if record.execution_blocked is not True:
        return False

    if not 0 <= record.governance_score <= 100:
        return False

    if record.governance_state not in {
        "GOVERNANCE_CONSOLIDATED",
        "GOVERNANCE_HOLD",
    }:
        return False

    return record.digest == _digest(data)
