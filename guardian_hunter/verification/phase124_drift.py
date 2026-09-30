"""Phase 124 — Defensive baseline drift detection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineDriftCheck:
    baseline_state: str
    baseline_score: int
    expected_state: str
    expected_score: int = 100

    @property
    def state(self) -> str:
        valid = (
            self.baseline_state == self.expected_state
            and self.baseline_score == self.expected_score
        )

        return (
            "DEFENSIVE_BASELINE_DRIFT_FREE"
            if valid
            else "DEFENSIVE_BASELINE_DRIFT_DETECTED"
        )

    @property
    def score(self) -> int:
        return 100 if self.state == "DEFENSIVE_BASELINE_DRIFT_FREE" else 0


def check_baseline(
    baseline_state: str,
    baseline_score: int,
) -> BaselineDriftCheck:
    return BaselineDriftCheck(
        baseline_state=baseline_state,
        baseline_score=baseline_score,
        expected_state="DEFENSIVE_OPERATIONAL_BASELINE_VALID",
    )
