"""Phase 37 — Defensive Security Continuity."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityContinuity:
    safeguards: Dict[str, bool]
    total_safeguards: int
    active_safeguards: int
    inactive_safeguards: int
    continuity_score: int
    continuity_ready: bool
    response_locked: bool
    mode: str
    execution_allowed: bool
    status: str


def build_security_continuity(
    safeguards: Dict[str, bool],
) -> SecurityContinuity:

    normalized = {
        str(key): bool(value)
        for key, value in safeguards.items()
    }

    total = len(normalized)

    active = sum(
        1 for value in normalized.values()
        if value
    )

    inactive = total - active

    score = (
        int((active / total) * 100)
        if total
        else 0
    )

    ready = (
        total > 0
        and inactive == 0
    )

    return SecurityContinuity(
        safeguards=normalized,
        total_safeguards=total,
        active_safeguards=active,
        inactive_safeguards=inactive,
        continuity_score=score,
        continuity_ready=ready,
        response_locked=True,
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "CONTINUITY_READY"
            if ready
            else "CONTINUITY_HOLD"
        ),
    )


def continuity_to_dict(
    continuity: SecurityContinuity,
) -> Dict[str, Any]:
    return asdict(continuity)


def validate_security_continuity(
    continuity: SecurityContinuity,
) -> bool:
    return (
        isinstance(continuity, SecurityContinuity)
        and continuity.total_safeguards
        == len(continuity.safeguards)
        and continuity.active_safeguards
        + continuity.inactive_safeguards
        == continuity.total_safeguards
        and 0 <= continuity.continuity_score <= 100
        and continuity.continuity_ready
        == (
            continuity.total_safeguards > 0
            and continuity.inactive_safeguards == 0
        )
        and continuity.response_locked is True
        and continuity.mode == "READ_ONLY"
        and continuity.execution_allowed is False
    )
