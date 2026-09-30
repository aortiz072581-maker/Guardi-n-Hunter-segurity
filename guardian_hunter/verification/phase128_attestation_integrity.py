"""Phase 128 — Defensive attestation integrity."""

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class AttestationIntegrity:
    attestation_state: str
    attestation_score: int
    digest: str

    @property
    def state(self) -> str:
        valid = (
            self.attestation_state == "DEFENSIVE_STATE_ATTESTATION_VALID"
            and self.attestation_score == 100
            and len(self.digest) == 64
        )
        return (
            "DEFENSIVE_ATTESTATION_INTEGRITY_VALID"
            if valid
            else "DEFENSIVE_ATTESTATION_INTEGRITY_INVALID"
        )

    @property
    def score(self) -> int:
        return 100 if self.state == "DEFENSIVE_ATTESTATION_INTEGRITY_VALID" else 0


def build_integrity(attestation_state: str, attestation_score: int):
    payload = {
        "attestation_state": attestation_state,
        "attestation_score": attestation_score,
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    digest = hashlib.sha256(canonical).hexdigest()

    return AttestationIntegrity(
        attestation_state=attestation_state,
        attestation_score=attestation_score,
        digest=digest,
    )
