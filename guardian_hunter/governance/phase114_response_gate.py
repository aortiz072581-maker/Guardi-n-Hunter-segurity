"""Phase 114 — Defensive Response Final Governance Gate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseReleaseGate:
    governance_state: str
    verification_state: str
    audit_state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False
    human_review_required: bool = True
    response_locked: bool = True

    @property
    def state(self) -> str:
        valid = (
            self.governance_state
            == "DEFENSIVE_RESPONSE_GOVERNANCE_HARDENED"
            and self.verification_state
            == "DEFENSIVE_RESPONSE_VERIFICATION_CHAIN_VALID"
            and self.audit_state
            == "DEFENSIVE_RESPONSE_AUDIT_CONTINUOUS"
            and self.read_only
            and self.dry_run
            and not self.execution_allowed
            and self.human_review_required
            and self.response_locked
        )

        return (
            "DEFENSIVE_RESPONSE_RELEASE_GATE_READY"
            if valid
            else "DEFENSIVE_RESPONSE_RELEASE_GATE_BLOCKED"
        )

    @property
    def score(self) -> int:
        return 100 if self.state == "DEFENSIVE_RESPONSE_RELEASE_GATE_READY" else 0


def build_release_gate(
    governance_state: str,
    verification_state: str,
    audit_state: str,
) -> ResponseReleaseGate:
    return ResponseReleaseGate(
        governance_state=governance_state,
        verification_state=verification_state,
        audit_state=audit_state,
    )
