"""Phase 129 — Defensive governance consistency lock."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GovernanceConsistencyLock:
    attestation_state: str
    integrity_state: str

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
            and self.read_only
            and self.dry_run
            and self.human_review_required
            and self.response_locked
            and self.real_execution_blocked
        )
        return (
            "DEFENSIVE_GOVERNANCE_CONSISTENCY_LOCKED"
            if valid
            else "DEFENSIVE_GOVERNANCE_CONSISTENCY_UNLOCKED"
        )

    @property
    def score(self) -> int:
        return (
            100
            if self.state == "DEFENSIVE_GOVERNANCE_CONSISTENCY_LOCKED"
            else 0
        )


def build_consistency_lock(
    attestation_state: str,
    integrity_state: str,
) -> GovernanceConsistencyLock:
    return GovernanceConsistencyLock(
        attestation_state=attestation_state,
        integrity_state=integrity_state,
    )
