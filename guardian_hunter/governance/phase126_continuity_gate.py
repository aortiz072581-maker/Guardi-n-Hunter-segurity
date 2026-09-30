"""Phase 126 — Defensive continuity gate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DefensiveContinuityGate:
    baseline_state: str
    drift_state: str
    policy_state: str

    response_score: int = 100
    read_only: bool = True
    dry_run: bool = True
    human_review_required: bool = True
    response_locked: bool = True
    real_execution_blocked: bool = True

    @property
    def state(self) -> str:
        valid = (
            self.baseline_state
            == "DEFENSIVE_OPERATIONAL_BASELINE_VALID"
            and self.drift_state
            == "DEFENSIVE_BASELINE_DRIFT_FREE"
            and self.policy_state
            == "DEFENSIVE_POLICY_LOCK_VALID"
            and self.response_score == 100
            and self.read_only
            and self.dry_run
            and self.human_review_required
            and self.response_locked
            and self.real_execution_blocked
        )

        return (
            "DEFENSIVE_CONTINUITY_GATE_READY"
            if valid
            else "DEFENSIVE_CONTINUITY_GATE_BLOCKED"
        )

    @property
    def score(self) -> int:
        return 100 if self.state == "DEFENSIVE_CONTINUITY_GATE_READY" else 0


def build_continuity_gate(
    baseline_state: str,
    drift_state: str,
    policy_state: str,
) -> DefensiveContinuityGate:
    return DefensiveContinuityGate(
        baseline_state=baseline_state,
        drift_state=drift_state,
        policy_state=policy_state,
    )
