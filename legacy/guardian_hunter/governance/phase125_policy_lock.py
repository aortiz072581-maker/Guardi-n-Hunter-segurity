"""Phase 125 — Defensive policy lock."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DefensivePolicyLock:
    read_only: bool = True
    dry_run: bool = True
    human_review_required: bool = True
    response_locked: bool = True
    real_execution_blocked: bool = True

    @property
    def state(self) -> str:
        valid = (
            self.read_only
            and self.dry_run
            and self.human_review_required
            and self.response_locked
            and self.real_execution_blocked
        )

        return (
            "DEFENSIVE_POLICY_LOCK_VALID"
            if valid
            else "DEFENSIVE_POLICY_LOCK_INVALID"
        )

    @property
    def score(self) -> int:
        return 100 if self.state == "DEFENSIVE_POLICY_LOCK_VALID" else 0


def build_policy_lock() -> DefensivePolicyLock:
    return DefensivePolicyLock()
