"""Immutable security findings for the supervised Guardian auditor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Confidence(str, Enum):
    CONFIRMED = "CONFIRMED"
    LIKELY = "LIKELY"
    POSSIBLE = "POSSIBLE"
    FALSE_POSITIVE = "FALSE_POSITIVE"


@dataclass(frozen=True)
class Finding:
    finding_id: str
    severity: Severity
    confidence: Confidence
    title: str
    description: str
    risk: str
    evidence: tuple[str, ...]
    affected_files: tuple[str, ...]
    proposed_fix: str
    required_tests: tuple[str, ...]

    # Security invariants.
    automatic_repair: bool = False
    automatic_approval: bool = False
    execution_allowed: bool = False
    merge_allowed: bool = False
    human_approval_required: bool = True

    def validate(self) -> None:
        if not self.finding_id.startswith("GH-"):
            raise ValueError("INVALID_FINDING_ID")

        if not self.title.strip():
            raise ValueError("EMPTY_FINDING_TITLE")

        if not self.description.strip():
            raise ValueError("EMPTY_FINDING_DESCRIPTION")

        if not self.risk.strip():
            raise ValueError("EMPTY_FINDING_RISK")

        if not self.evidence:
            raise ValueError("EVIDENCE_REQUIRED")

        if not self.affected_files:
            raise ValueError("AFFECTED_FILES_REQUIRED")

        if not self.proposed_fix.strip():
            raise ValueError("PROPOSED_FIX_REQUIRED")

        if not self.required_tests:
            raise ValueError("REQUIRED_TESTS_REQUIRED")

        if self.automatic_repair:
            raise PermissionError("AUTOMATIC_REPAIR_FORBIDDEN")

        if self.automatic_approval:
            raise PermissionError("AUTOMATIC_APPROVAL_FORBIDDEN")

        if self.execution_allowed:
            raise PermissionError("AUDITOR_EXECUTION_FORBIDDEN")

        if self.merge_allowed:
            raise PermissionError("AUDITOR_MERGE_FORBIDDEN")

        if not self.human_approval_required:
            raise PermissionError("HUMAN_APPROVAL_REQUIRED")


def validate_findings(findings: tuple[Finding, ...]) -> bool:
    seen: set[str] = set()

    for finding in findings:
        finding.validate()

        if finding.finding_id in seen:
            raise ValueError("DUPLICATE_FINDING_ID")

        seen.add(finding.finding_id)

    return True
