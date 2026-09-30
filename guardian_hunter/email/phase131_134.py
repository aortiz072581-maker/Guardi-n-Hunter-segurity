"""
Guardian Hunter — Phases 131 → 134
Isolation & Response

SAFE DESIGN:
- READ_ONLY=True
- DRY_RUN=True
- REAL_EXECUTION_BLOCKED=True
- HUMAN_REVIEW_REQUIRED=True
- RESPONSE_LOCKED=True

Isolation is logical only.
No files are deleted, moved, executed, or modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass
class EvidenceRecord:
    event: str
    timestamp: str
    severity: str
    subject: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class IsolationRecord:
    subject: str
    isolation_requested: bool
    isolation_active: bool
    physical_action_performed: bool
    reason: str


@dataclass
class DefensiveResponse:
    blocked: bool
    isolation: IsolationRecord
    human_review_required: bool
    response_locked: bool
    execution_allowed: bool
    dry_run: bool
    read_only: bool
    evidence: list[EvidenceRecord]
    response_state: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(subject: str) -> str:
    return sha256(subject.encode("utf-8")).hexdigest()


def create_evidence(
    event: str,
    severity: str,
    subject: str,
    evidence: dict[str, Any] | None = None,
) -> EvidenceRecord:

    return EvidenceRecord(
        event=event,
        timestamp=_now(),
        severity=severity,
        subject=subject,
        evidence=evidence or {},
    )


def isolate_subject(
    subject: str,
    reason: str,
) -> IsolationRecord:
    """
    Logical quarantine only.

    IMPORTANT:
    No filesystem operation is performed.
    """

    return IsolationRecord(
        subject=subject,
        isolation_requested=True,
        isolation_active=True,
        physical_action_performed=False,
        reason=reason,
    )


def build_defensive_response(
    subject: str,
    risk_level: str,
    findings: list[dict[str, Any]] | None = None,
) -> DefensiveResponse:

    findings = findings or []

    critical = risk_level.upper() in {"CRITICAL", "HIGH"}

    blocked = critical or bool(findings)

    evidence: list[EvidenceRecord] = []

    evidence.append(
        create_evidence(
            event="SECURITY_ASSESSMENT",
            severity=risk_level.upper(),
            subject=subject,
            evidence={
                "finding_count": len(findings),
                "read_only": READ_ONLY,
                "dry_run": DRY_RUN,
            },
        )
    )

    if blocked:
        isolation = isolate_subject(
            subject=subject,
            reason="Security policy requires logical isolation",
        )

        evidence.append(
            create_evidence(
                event="LOGICAL_ISOLATION",
                severity="HIGH",
                subject=subject,
                evidence={
                    "isolation_active": isolation.isolation_active,
                    "physical_action_performed": False,
                },
            )
        )

        evidence.append(
            create_evidence(
                event="RESPONSE_BLOCKED",
                severity="HIGH",
                subject=subject,
                evidence={
                    "execution_allowed": False,
                    "human_review_required": True,
                    "response_locked": True,
                },
            )
        )

        response_state = "ISOLATED_REVIEW_REQUIRED"

    else:
        isolation = IsolationRecord(
            subject=subject,
            isolation_requested=False,
            isolation_active=False,
            physical_action_performed=False,
            reason="No blocking condition detected",
        )

        evidence.append(
            create_evidence(
                event="SECURITY_ASSESSMENT_CLEAN",
                severity="INFO",
                subject=subject,
            )
        )

        response_state = "MONITORED"

    return DefensiveResponse(
        blocked=blocked,
        isolation=isolation,
        human_review_required=HUMAN_REVIEW_REQUIRED,
        response_locked=RESPONSE_LOCKED,
        execution_allowed=False,
        dry_run=DRY_RUN,
        read_only=READ_ONLY,
        evidence=evidence,
        response_state=response_state,
    )


def export_evidence(response: DefensiveResponse) -> list[dict[str, Any]]:
    """
    Converts evidence to immutable-style dictionaries.

    No disk write is performed.
    """

    return [
        {
            "event": item.event,
            "timestamp": item.timestamp,
            "severity": item.severity,
            "subject": item.subject,
            "evidence": dict(item.evidence),
        }
        for item in response.evidence
    ]


def security_digest(response: DefensiveResponse) -> str:
    """
    Produces a deterministic digest of the response evidence.
    """

    serialized = repr(export_evidence(response)).encode("utf-8")

    return sha256(serialized).hexdigest()
