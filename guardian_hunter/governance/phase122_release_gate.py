"""Phase 122 — Defensive Release Continuity Gate."""

from dataclasses import dataclass

from guardian_hunter.governance.phase115_state_snapshot import (
    StateSnapshot,
)
from guardian_hunter.verification.phase119_integrity_chain import (
    IntegrityChainResult,
)
from guardian_hunter.governance.phase120_tamper_gate import (
    TamperGateResult,
)
from guardian_hunter.verification.phase121_safety_consistency import (
    SafetyConsistencyResult,
)


@dataclass(frozen=True)
class ReleaseContinuityResult:
    state: str
    score: int
    ready: bool
    integrity_valid: bool
    tamper_gate_valid: bool
    cross_phase_consistent: bool
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool


def build_release_continuity(
    snapshot: StateSnapshot,
    integrity: IntegrityChainResult,
    tamper_gate: TamperGateResult,
    consistency: SafetyConsistencyResult,
) -> ReleaseContinuityResult:

    ready = (
        snapshot.score >= 100
        and integrity.score >= 100
        and tamper_gate.score >= 100
        and consistency.score >= 100
        and integrity.valid is True
        and tamper_gate.clean is True
        and consistency.consistent is True
        and snapshot.read_only is True
        and snapshot.dry_run is True
        and snapshot.real_execution_blocked is True
        and snapshot.human_review_required is True
        and snapshot.response_locked is True
    )

    return ReleaseContinuityResult(
        state=(
            "DEFENSIVE_RELEASE_CONTINUITY_READY"
            if ready
            else "DEFENSIVE_RELEASE_CONTINUITY_BLOCKED"
        ),
        score=100 if ready else 0,
        ready=ready,
        integrity_valid=integrity.valid,
        tamper_gate_valid=tamper_gate.clean,
        cross_phase_consistent=consistency.consistent,
        read_only=snapshot.read_only,
        dry_run=snapshot.dry_run,
        real_execution_blocked=snapshot.real_execution_blocked,
        human_review_required=snapshot.human_review_required,
        response_locked=snapshot.response_locked,
    )
