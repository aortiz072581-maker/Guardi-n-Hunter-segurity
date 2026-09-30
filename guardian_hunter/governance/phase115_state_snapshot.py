"""Phase 115 — Immutable Defensive State Snapshot."""

from dataclasses import dataclass
from typing import Any, Mapping
import json
import hashlib


@dataclass(frozen=True)
class StateSnapshot:
    state: str
    score: int
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool
    digest: str


def _canonical_payload(
    state: str,
    score: int,
    read_only: bool,
    dry_run: bool,
    real_execution_blocked: bool,
    human_review_required: bool,
    response_locked: bool,
) -> bytes:
    payload = {
        "state": state,
        "score": score,
        "READ_ONLY": read_only,
        "DRY_RUN": dry_run,
        "REAL_EXECUTION_BLOCKED": real_execution_blocked,
        "HUMAN_REVIEW_REQUIRED": human_review_required,
        "RESPONSE_LOCKED": response_locked,
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build_state_snapshot(
    *,
    state: str,
    score: int,
    read_only: bool = True,
    dry_run: bool = True,
    real_execution_blocked: bool = True,
    human_review_required: bool = True,
    response_locked: bool = True,
) -> StateSnapshot:

    digest = hashlib.sha256(
        _canonical_payload(
            state,
            score,
            read_only,
            dry_run,
            real_execution_blocked,
            human_review_required,
            response_locked,
        )
    ).hexdigest()

    return StateSnapshot(
        state=state,
        score=score,
        read_only=read_only,
        dry_run=dry_run,
        real_execution_blocked=real_execution_blocked,
        human_review_required=human_review_required,
        response_locked=response_locked,
        digest=digest,
    )


def snapshot_from_mapping(data: Mapping[str, Any]) -> StateSnapshot:
    return build_state_snapshot(
        state=str(data["state"]),
        score=int(data["score"]),
        read_only=bool(data.get("READ_ONLY", True)),
        dry_run=bool(data.get("DRY_RUN", True)),
        real_execution_blocked=bool(
            data.get("REAL_EXECUTION_BLOCKED", True)
        ),
        human_review_required=bool(
            data.get("HUMAN_REVIEW_REQUIRED", True)
        ),
        response_locked=bool(
            data.get("RESPONSE_LOCKED", True)
        ),
    )
