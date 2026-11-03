"""Phase 40 — Defensive Security Decision Record."""

from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict
import json

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityDecisionRecord:
    posture_ready: bool
    posture_score: int
    decision: str
    requires_human_review: bool
    evidence_required: bool
    response_locked: bool
    execution_allowed: bool
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


def build_security_decision(
    posture_ready: bool,
    posture_score: int,
) -> SecurityDecisionRecord:

    ready = bool(posture_ready)
    score = max(0, min(100, int(posture_score)))

    if ready and score >= 90:
        decision = "CONTINUE_DEFENSIVE_MONITORING"
        review = False
        evidence = False
    elif score >= 70:
        decision = "ENHANCED_DEFENSIVE_MONITORING"
        review = True
        evidence = True
    else:
        decision = "HOLD_AND_VALIDATE"
        review = True
        evidence = True

    if not ready:
        decision = "HOLD_AND_VALIDATE"
        review = True
        evidence = True

    payload = {
        "posture_ready": ready,
        "posture_score": score,
        "decision": decision,
        "requires_human_review": review,
        "evidence_required": evidence,
        "response_locked": True,
        "execution_allowed": False,
        "mode": "READ_ONLY",
    }

    return SecurityDecisionRecord(
        posture_ready=ready,
        posture_score=score,
        decision=decision,
        requires_human_review=review,
        evidence_required=evidence,
        response_locked=True,
        execution_allowed=False,
        digest=_digest(payload),
        mode="READ_ONLY",
        status="DEFENSIVE_DECISION_ONLY",
    )


def decision_to_dict(
    decision: SecurityDecisionRecord,
) -> Dict[str, Any]:
    return asdict(decision)


def validate_security_decision(
    decision: SecurityDecisionRecord,
) -> bool:
    return (
        isinstance(decision, SecurityDecisionRecord)
        and 0 <= decision.posture_score <= 100
        and decision.response_locked is True
        and decision.execution_allowed is False
        and decision.mode == "READ_ONLY"
        and decision.status == "DEFENSIVE_DECISION_ONLY"
        and len(decision.digest) == 64
    )
