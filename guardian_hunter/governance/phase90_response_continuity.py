"""Phase 90 — Defensive Response Continuity
Final continuity gate for phases 87 → 90.
"""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveResponseContinuity:
    score: int
    state: str
    continuity_valid: bool
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
    return sha256(_canonical(data).encode("utf-8")).hexdigest()


def build_response_continuity(
    score: int = 100,
    assurance_valid: bool = True,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> DefensiveResponseContinuity:

    score = max(0, min(100, int(score)))

    continuity_valid = (
        score == 100
        and assurance_valid is True
        and response_locked is True
        and human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and EXECUTION_ALLOWED is False
    )

    state = (
        "DEFENSIVE_RESPONSE_CONTINUOUS"
        if continuity_valid
        else "DEFENSIVE_RESPONSE_CONTINUITY_HOLD"
    )

    payload = {
        "score": score if continuity_valid else min(score, 99),
        "state": state,
        "continuity_valid": continuity_valid,
        "response_locked": bool(response_locked),
        "human_review_required": bool(human_review_required),
        "read_only": READ_ONLY,
        "dry_run": DRY_RUN,
        "execution_allowed": EXECUTION_ALLOWED,
    }

    return DefensiveResponseContinuity(
        score=payload["score"],
        state=state,
        continuity_valid=continuity_valid,
        digest=_digest(payload),
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def response_continuity_to_dict(
    result: DefensiveResponseContinuity,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_continuity(
    result: DefensiveResponseContinuity,
) -> bool:
    if not isinstance(result, DefensiveResponseContinuity):
        return False

    if not (0 <= result.score <= 100):
        return False

    if result.state != "DEFENSIVE_RESPONSE_CONTINUOUS":
        return False

    if result.continuity_valid is not True:
        return False

    if not result.digest or len(result.digest) != 64:
        return False

    return (
        result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
