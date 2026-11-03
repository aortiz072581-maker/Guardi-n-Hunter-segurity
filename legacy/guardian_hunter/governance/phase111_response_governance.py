"""Phase 111 — Defensive Response Governance Hardening."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseGovernance:
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False
    human_review_required: bool = True
    response_locked: bool = True

    @property
    def state(self) -> str:
        if (
            self.read_only
            and self.dry_run
            and not self.execution_allowed
            and self.human_review_required
            and self.response_locked
        ):
            return "DEFENSIVE_RESPONSE_GOVERNANCE_HARDENED"
        return "DEFENSIVE_RESPONSE_GOVERNANCE_INVALID"

    @property
    def score(self) -> int:
        checks = (
            self.read_only,
            self.dry_run,
            not self.execution_allowed,
            self.human_review_required,
            self.response_locked,
        )
        return 100 if all(checks) else 0


def build_response_governance() -> ResponseGovernance:
    return ResponseGovernance()
