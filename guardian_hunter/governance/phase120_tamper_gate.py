"""Phase 120 — Defensive Tamper Consistency Gate."""

from dataclasses import dataclass

from guardian_hunter.verification.phase119_integrity_chain import (
    IntegrityChainResult,
)


@dataclass(frozen=True)
class TamperGateResult:
    state: str
    score: int
    clean: bool
    integrity_valid: bool
    tamper_detected: bool
    execution_blocked: bool
    human_review_required: bool
    response_locked: bool


def validate_tamper_gate(
    integrity: IntegrityChainResult,
    *,
    tamper_detected: bool = False,
    execution_blocked: bool = True,
    human_review_required: bool = True,
    response_locked: bool = True,
) -> TamperGateResult:

    clean = (
        integrity.valid
        and tamper_detected is False
        and execution_blocked is True
        and human_review_required is True
        and response_locked is True
    )

    return TamperGateResult(
        state=(
            "DEFENSIVE_TAMPER_GATE_CLEAN"
            if clean
            else "DEFENSIVE_TAMPER_GATE_BLOCKED"
        ),
        score=100 if clean else 0,
        clean=clean,
        integrity_valid=integrity.valid,
        tamper_detected=tamper_detected,
        execution_blocked=execution_blocked,
        human_review_required=human_review_required,
        response_locked=response_locked,
    )
