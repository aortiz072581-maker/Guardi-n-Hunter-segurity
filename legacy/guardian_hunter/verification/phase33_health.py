"""Phase 33 — Defensive Security Health Gate."""

from dataclasses import dataclass, asdict
from typing import Any, Dict

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityHealthGate:
    governance_ok: bool
    verification_ok: bool
    audit_ok: bool
    evidence_ok: bool
    baseline_ok: bool
    response_locked: bool
    health_score: int
    healthy: bool
    mode: str
    execution_allowed: bool
    status: str


def build_security_health_gate(
    governance_ok: bool,
    verification_ok: bool,
    audit_ok: bool,
    evidence_ok: bool,
    baseline_ok: bool,
    response_locked: bool,
) -> SecurityHealthGate:

    controls = [
        bool(governance_ok),
        bool(verification_ok),
        bool(audit_ok),
        bool(evidence_ok),
        bool(baseline_ok),
        bool(response_locked),
    ]

    score = int(
        (sum(controls) / len(controls)) * 100
    )

    healthy = all(controls)

    return SecurityHealthGate(
        governance_ok=bool(governance_ok),
        verification_ok=bool(verification_ok),
        audit_ok=bool(audit_ok),
        evidence_ok=bool(evidence_ok),
        baseline_ok=bool(baseline_ok),
        response_locked=bool(response_locked),
        health_score=score,
        healthy=healthy,
        mode="READ_ONLY",
        execution_allowed=False,
        status=(
            "HEALTHY_READ_ONLY"
            if healthy
            else "HEALTH_HOLD"
        ),
    )


def health_to_dict(
    health: SecurityHealthGate,
) -> Dict[str, Any]:
    return asdict(health)


def validate_security_health(
    health: SecurityHealthGate,
) -> bool:
    return (
        isinstance(health, SecurityHealthGate)
        and 0 <= health.health_score <= 100
        and health.healthy
        == (
            health.governance_ok
            and health.verification_ok
            and health.audit_ok
            and health.evidence_ok
            and health.baseline_ok
            and health.response_locked
        )
        and health.mode == "READ_ONLY"
        and health.execution_allowed is False
    )
