"""Phase 57 — Defensive Recovery Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class RecoveryGate:
    evidence_ready: bool
    alerts_ready: bool
    baseline_ready: bool
    audit_ready: bool
    recovery_allowed: bool
    human_review_required: bool
    execution_blocked: bool
    reason: str
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


def build_recovery_gate(
    evidence_ready,
    alerts_ready,
    baseline_ready,
    audit_ready,
):
    all_ready = all(
        [
            evidence_ready,
            alerts_ready,
            baseline_ready,
            audit_ready,
        ]
    )

    recovery_allowed = (
        all_ready
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    payload = RecoveryGate(
        evidence_ready=evidence_ready,
        alerts_ready=alerts_ready,
        baseline_ready=baseline_ready,
        audit_ready=audit_ready,
        recovery_allowed=recovery_allowed,
        human_review_required=True,
        execution_blocked=not EXECUTION_ALLOWED,
        reason=(
            "RECOVERY_PLAN_READY_FOR_REVIEW"
            if recovery_allowed
            else "RECOVERY_GATE_HOLD"
        ),
    )

    data = asdict(payload)
    data["digest"] = _digest(data)

    return RecoveryGate(**data)


def recovery_to_dict(gate):
    return asdict(gate)


def validate_recovery_gate(gate):
    if not isinstance(gate, RecoveryGate):
        return False

    data = asdict(gate)

    if gate.execution_blocked is not True:
        return False

    if gate.human_review_required is not True:
        return False

    if gate.recovery_allowed is not True:
        return False

    if not gate.reason:
        return False

    return gate.digest == _digest(data)
