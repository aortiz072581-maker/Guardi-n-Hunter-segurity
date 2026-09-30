"""Phase 75 — Defensive Evidence Readiness."""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveEvidenceReadiness:
    evidence_available: bool
    evidence_integrity_ok: bool
    evidence_traceable: bool
    audit_ready: bool
    evidence_ready: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def build_evidence_readiness(
    evidence_available=True,
    evidence_integrity_ok=True,
    evidence_traceable=True,
    audit_ready=True,
):
    evidence_ready = bool(
        evidence_available
        and evidence_integrity_ok
        and evidence_traceable
        and audit_ready
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if evidence_ready else 0

    state = (
        "DEFENSIVE_EVIDENCE_READY"
        if evidence_ready
        else "DEFENSIVE_EVIDENCE_BLOCKED"
    )

    return DefensiveEvidenceReadiness(
        evidence_available=bool(evidence_available),
        evidence_integrity_ok=bool(evidence_integrity_ok),
        evidence_traceable=bool(evidence_traceable),
        audit_ready=bool(audit_ready),
        evidence_ready=evidence_ready,
        score=score,
        state=state,
    )


def evidence_readiness_to_dict(record):
    return {
        "evidence_available": record.evidence_available,
        "evidence_integrity_ok": record.evidence_integrity_ok,
        "evidence_traceable": record.evidence_traceable,
        "audit_ready": record.audit_ready,
        "evidence_ready": record.evidence_ready,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_evidence_readiness(record):
    if not isinstance(record, DefensiveEvidenceReadiness):
        return False
    if record.score not in (0, 100):
        return False
    if record.evidence_ready and record.score != 100:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    return True
