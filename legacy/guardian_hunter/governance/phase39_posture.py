"""Phase 39 — Defensive Security Posture Snapshot."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityPostureSnapshot:
    controls_ok: bool
    integrity_ok: bool
    continuity_ok: bool
    operations_ok: bool
    audit_ok: bool
    evidence_ok: bool
    baseline_ok: bool
    response_locked: bool
    posture_score: int
    posture_ready: bool
    digest: str
    mode: str
    execution_allowed: bool
    status: str


def _canonical(data: Dict[str, Any]) -> str:
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


def build_posture_snapshot(
    controls_ok: bool,
    integrity_ok: bool,
    continuity_ok: bool,
    operations_ok: bool,
    audit_ok: bool,
    evidence_ok: bool,
    baseline_ok: bool,
    response_locked: bool,
) -> SecurityPostureSnapshot:

    checks = [
        bool(controls_ok),
        bool(integrity_ok),
        bool(continuity_ok),
        bool(operations_ok),
        bool(audit_ok),
        bool(evidence_ok),
        bool(baseline_ok),
        bool(response_locked),
    ]

    score = int((sum(checks) / len(checks)) * 100)
    ready = all(checks)

    payload = {
        "controls_ok": bool(controls_ok),
        "integrity_ok": bool(integrity_ok),
        "continuity_ok": bool(continuity_ok),
        "operations_ok": bool(operations_ok),
        "audit_ok": bool(audit_ok),
        "evidence_ok": bool(evidence_ok),
        "baseline_ok": bool(baseline_ok),
        "response_locked": bool(response_locked),
        "posture_score": score,
        "posture_ready": ready,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }

    return SecurityPostureSnapshot(
        controls_ok=bool(controls_ok),
        integrity_ok=bool(integrity_ok),
        continuity_ok=bool(continuity_ok),
        operations_ok=bool(operations_ok),
        audit_ok=bool(audit_ok),
        evidence_ok=bool(evidence_ok),
        baseline_ok=bool(baseline_ok),
        response_locked=bool(response_locked),
        posture_score=score,
        posture_ready=ready,
        digest=_digest(payload),
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "SECURITY_POSTURE_READY"
            if ready
            else "SECURITY_POSTURE_HOLD"
        ),
    )


def posture_to_dict(
    posture: SecurityPostureSnapshot,
) -> Dict[str, Any]:
    return asdict(posture)


def validate_posture(
    posture: SecurityPostureSnapshot,
) -> bool:
    return (
        isinstance(posture, SecurityPostureSnapshot)
        and 0 <= posture.posture_score <= 100
        and posture.posture_ready == (
            posture.controls_ok
            and posture.integrity_ok
            and posture.continuity_ok
            and posture.operations_ok
            and posture.audit_ok
            and posture.evidence_ok
            and posture.baseline_ok
            and posture.response_locked
        )
        and len(posture.digest) == 64
        and posture.mode == "READ_ONLY"
        and posture.execution_allowed is False
    )
