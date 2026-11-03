"""Phase 49 — Defensive Security Posture Snapshot."""

from dataclasses import dataclass


@dataclass
class SecurityPosture:
    case_state: str
    risk_score: float
    readiness: str
    compliance: str
    audit_events: int
    baseline_integrity: bool
    execution_allowed: bool = False


def build_security_posture(
    *,
    case_state: str,
    risk_score: float,
    readiness: str,
    compliance: str,
    audit_events: int,
    baseline_integrity: bool,
) -> SecurityPosture:
    return SecurityPosture(
        case_state=case_state,
        risk_score=float(risk_score),
        readiness=readiness,
        compliance=compliance,
        audit_events=int(audit_events),
        baseline_integrity=bool(baseline_integrity),
        execution_allowed=False,
    )


def validate_security_posture(posture: SecurityPosture) -> bool:
    return (
        0.0 <= posture.risk_score <= 100.0
        and posture.audit_events >= 0
        and posture.baseline_integrity in {True, False}
        and posture.execution_allowed is False
    )


def build_posture_report(posture: SecurityPosture) -> dict:
    return {
        "phase": 49,
        "case_state": posture.case_state,
        "risk_score": posture.risk_score,
        "readiness": posture.readiness,
        "compliance": posture.compliance,
        "audit_events": posture.audit_events,
        "baseline_integrity": posture.baseline_integrity,
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
