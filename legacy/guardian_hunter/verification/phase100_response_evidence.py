"""Phase 100 — Defensive Response Evidence Reconciliation."""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseEvidence:
    score: int
    state: str
    evidence_valid: bool
    digest: str
    response_locked: bool
    human_review_required: bool
    read_only: bool
    dry_run: bool
    execution_allowed: bool


def _canonical(data: Dict[str, Any]) -> str:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(data: Dict[str, Any]) -> str:
    return sha256(
        _canonical(data).encode("utf-8")
    ).hexdigest()


def build_response_evidence(
    score: int = 100,
    control_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseEvidence:

    score = max(0, min(100, int(score)))

    valid = (
        score == 100
        and control_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    state = (
        "DEFENSIVE_RESPONSE_EVIDENCE_RECONCILED"
        if valid
        else "DEFENSIVE_RESPONSE_EVIDENCE_HOLD"
    )

    payload = {
        "score": score if valid else min(score, 99),
        "state": state,
        "evidence_valid": valid,
        "response_locked": bool(response_locked),
        "human_review_required": bool(human_review_required),
        "read_only": READ_ONLY,
        "dry_run": DRY_RUN,
        "execution_allowed": EXECUTION_ALLOWED,
    }

    return DefensiveResponseEvidence(
        score=payload["score"],
        state=state,
        evidence_valid=valid,
        digest=_digest(payload),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def evidence_to_dict(
    result: DefensiveResponseEvidence,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_evidence(
    result: DefensiveResponseEvidence,
) -> bool:
    return (
        isinstance(result, DefensiveResponseEvidence)
        and result.score == 100
        and result.state == "DEFENSIVE_RESPONSE_EVIDENCE_RECONCILED"
        and result.evidence_valid is True
        and len(result.digest) == 64
        and result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
