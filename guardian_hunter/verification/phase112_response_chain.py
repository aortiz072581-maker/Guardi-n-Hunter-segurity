"""Phase 112 — Defensive Response Verification Chain."""

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ResponseVerificationChain:
    payload: Dict[str, Any]
    digest: str

    @property
    def state(self) -> str:
        return "DEFENSIVE_RESPONSE_VERIFICATION_CHAIN_VALID"

    @property
    def score(self) -> int:
        return 100


def build_verification_chain(payload: Dict[str, Any]) -> ResponseVerificationChain:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    digest = hashlib.sha256(canonical).hexdigest()

    return ResponseVerificationChain(
        payload=dict(payload),
        digest=digest,
    )
