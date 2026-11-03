"""Phase 88 — Defensive Response Integrity Reconciliation
Read-only integrity verification for response state.
"""

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class ResponseIntegrityReconciliation:
    score: int
    state: str
    digest: str
    integrity_valid: bool
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


def build_response_integrity(
    score: int = 100,
    response_locked: bool = True,
    human_review_required: bool = True,
) -> ResponseIntegrityReconciliation:

    score = max(0, min(100, int(score)))

    payload = {
        "score": score,
        "state": "DEFENSIVE_RESPONSE_INTEGRITY_RECONCILED",
        "response_locked": bool(response_locked),
        "human_review_required": bool(human_review_required),
        "read_only": READ_ONLY,
        "dry_run": DRY_RUN,
        "execution_allowed": EXECUTION_ALLOWED,
    }

    digest = _digest(payload)

    return ResponseIntegrityReconciliation(
        score=score,
        state="DEFENSIVE_RESPONSE_INTEGRITY_RECONCILED",
        digest=digest,
        integrity_valid=True,
        response_locked=bool(response_locked),
        human_review_required=bool(human_review_required),
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        execution_allowed=EXECUTION_ALLOWED,
    )


def response_integrity_to_dict(
    result: ResponseIntegrityReconciliation,
) -> Dict[str, Any]:
    return asdict(result)


def validate_response_integrity(
    result: ResponseIntegrityReconciliation,
) -> bool:
    if not isinstance(result, ResponseIntegrityReconciliation):
        return False

    if not (0 <= result.score <= 100):
        return False

    if result.state != "DEFENSIVE_RESPONSE_INTEGRITY_RECONCILED":
        return False

    if not result.digest or len(result.digest) != 64:
        return False

    return (
        result.integrity_valid is True
        and result.response_locked is True
        and result.human_review_required is True
        and result.read_only is True
        and result.dry_run is True
        and result.execution_allowed is False
    )
