"""Phase 83 — Defensive Signal Continuity."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveSignalContinuity:
    signals_available: bool
    signals_integrity_ok: bool
    signals_traceable: bool
    correlation_ready: bool
    continuity_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_signal_continuity(
    signals_available=True,
    signals_integrity_ok=True,
    signals_traceable=True,
    correlation_ready=True,
):
    continuity_valid = bool(
        signals_available
        and signals_integrity_ok
        and signals_traceable
        and correlation_ready
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if continuity_valid else 0

    state = (
        "DEFENSIVE_SIGNAL_CONTINUOUS"
        if continuity_valid
        else "DEFENSIVE_SIGNAL_BLOCKED"
    )

    return DefensiveSignalContinuity(
        signals_available=bool(signals_available),
        signals_integrity_ok=bool(signals_integrity_ok),
        signals_traceable=bool(signals_traceable),
        correlation_ready=bool(correlation_ready),
        continuity_valid=continuity_valid,
        score=score,
        state=state,
    )


def signal_to_dict(record):
    return {
        "signals_available": record.signals_available,
        "signals_integrity_ok": record.signals_integrity_ok,
        "signals_traceable": record.signals_traceable,
        "correlation_ready": record.correlation_ready,
        "continuity_valid": record.continuity_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_signal_continuity(record):
    if not isinstance(record, DefensiveSignalContinuity):
        return False
    if record.score not in (0, 100):
        return False
    if record.continuity_valid and record.score != 100:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    return True
