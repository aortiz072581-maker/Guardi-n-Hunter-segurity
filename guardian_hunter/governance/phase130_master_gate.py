"""Phase 130 — Defensive attestation master gate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AttestationMasterGate:
    attestation_state: str
    integrity_state: str
    consistency_state: str

    response_score: int = 100
    read_only: bool = True
    dry_run: bool = True
    human_review_required: bool = True
    response_locked: bool = True
    real_execution_blocked: bool = True

    @property
    def state(self) -> str:
        valid = (
            self.attestation_state
            == "DEFENSIVE_STATE_ATTESTATION_VALID"
            and self.integrity_state
            == "DEFENSIVE_ATTESTATION_INTEGRITY_VALID"
            and self.consistency_state
            == "DEFENSIVE_GOVERNANCE_CONSISTENCY_LOCKED"
            and self.response_score == 100
            and self.read_only
            and self.dry_run
            and self.human_review_required
            and self.response_locked
            and self.real_execution_blocked
        )
        return (
            "DEFENSIVE_ATTESTATION_MASTER_READY"
            if valid
            else "DEFENSIVE_ATTESTATION_MASTER_BLOCKED"
        )

    @property
    def score(self) -> int:
        return (
            100
            if self.state == "DEFENSIVE_ATTESTATION_MASTER_READY"
            else 0
        )


def build_master_gate(
    attestation_state: str,
    integrity_state: str,
    consistency_state: str,
) -> AttestationMasterGate:
    return AttestationMasterGate(
        attestation_state=attestation_state,
        integrity_state=integrity_state,
        consistency_state=consistency_state,
    )
