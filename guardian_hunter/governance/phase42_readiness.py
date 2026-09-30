"""Phase 42 — Final Defensive Readiness Gate."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class FinalDefensiveReadiness:
    posture_ok: bool
    decision_ok: bool
    audit_ok: bool
    integrity_ok: bool
    response_locked: bool
    readiness_score: int
    ready_for_monitoring: bool
    execution_blocked: bool
    digest: str
    mode: str
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


def build_final_readiness(
    posture_ok: bool,
    decision_ok: bool,
    audit_ok: bool,
    integrity_ok: bool,
    response_locked: bool,
) -> FinalDefensiveReadiness:

    checks = [
        bool(posture_ok),
        bool(decision_ok),
        bool(audit_ok),
        bool(integrity_ok),
        bool(response_locked),
    ]

    score = int((sum(checks) / len(checks)) * 100)
    ready = all(checks)

    payload = {
        "posture_ok": bool(posture_ok),
        "decision_ok": bool(decision_ok),
        "audit_ok": bool(audit_ok),
        "integrity_ok": bool(integrity_ok),
        "response_locked": bool(response_locked),
        "readiness_score": score,
        "ready_for_monitoring": ready,
        "execution_blocked": True,
        "mode": "READ_ONLY",
    }

    return FinalDefensiveReadiness(
        posture_ok=bool(posture_ok),
        decision_ok=bool(decision_ok),
        audit_ok=bool(audit_ok),
        integrity_ok=bool(integrity_ok),
        response_locked=bool(response_locked),
        readiness_score=score,
        ready_for_monitoring=ready,
        execution_blocked=True,
        digest=_digest(payload),
        mode="READ_ONLY",
        status=(
            "READY_FOR_DEFENSIVE_MONITORING"
            if ready
            else "DEFENSIVE_READINESS_HOLD"
        ),
    )


def readiness_to_dict(
    readiness: FinalDefensiveReadiness,
) -> Dict[str, Any]:
    return asdict(readiness)


def validate_final_readiness(
    readiness: FinalDefensiveReadiness,
) -> bool:
    return (
        isinstance(
            readiness,
            FinalDefensiveReadiness,
        )
        and 0 <= readiness.readiness_score <= 100
        and readiness.ready_for_monitoring == (
            readiness.posture_ok
            and readiness.decision_ok
            and readiness.audit_ok
            and readiness.integrity_ok
            and readiness.response_locked
        )
        and readiness.execution_blocked is True
        and len(readiness.digest) == 64
        and readiness.mode == "READ_ONLY"
    )
