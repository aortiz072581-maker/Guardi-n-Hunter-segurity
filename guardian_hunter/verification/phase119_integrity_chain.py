"""Phase 119 — Defensive Integrity Chain."""

from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class IntegrityChainResult:
    state: str
    score: int
    valid: bool
    snapshot_digest: str
    chain_digest: str


def build_integrity_chain(
    *,
    snapshot_digest: str,
    state: str,
    score: int,
) -> IntegrityChainResult:

    payload = {
        "snapshot_digest": snapshot_digest,
        "state": state,
        "score": score,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    chain_digest = hashlib.sha256(canonical).hexdigest()

    valid = (
        bool(snapshot_digest)
        and len(snapshot_digest) == 64
        and score >= 100
    )

    return IntegrityChainResult(
        state=(
            "DEFENSIVE_INTEGRITY_CHAIN_VALID"
            if valid
            else "DEFENSIVE_INTEGRITY_CHAIN_BLOCKED"
        ),
        score=100 if valid else 0,
        valid=valid,
        snapshot_digest=snapshot_digest,
        chain_digest=chain_digest,
    )
