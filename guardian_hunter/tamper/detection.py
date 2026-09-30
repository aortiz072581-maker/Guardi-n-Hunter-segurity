"""
Guardian Hunter — Evasion & Tamper Detection v1

Defensive detection only.

Detects:
- file integrity drift,
- safety-state drift,
- authorization-state anomalies,
- evidence-chain anomalies,
- repeated failed transitions,
- unexpected configuration changes.

This module does NOT:
- execute commands,
- modify external systems,
- evade detection,
- retaliate,
- disable security controls.

All responses are signals/plans only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


class TamperSignal(str, Enum):
    FILE_INTEGRITY_DRIFT = "FILE_INTEGRITY_DRIFT"
    SAFETY_STATE_DRIFT = "SAFETY_STATE_DRIFT"
    AUTHORIZATION_ANOMALY = "AUTHORIZATION_ANOMALY"
    EVIDENCE_CHAIN_ANOMALY = "EVIDENCE_CHAIN_ANOMALY"
    REPEATED_FAILURES = "REPEATED_FAILURES"
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"


class TamperSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class TamperFinding:
    signal: TamperSignal
    severity: TamperSeverity
    target: str
    reason: str
    evidence: Mapping[str, Any]
    execution_allowed: bool = False


@dataclass(frozen=True)
class TamperAssessment:
    target: str
    findings: tuple[TamperFinding, ...]
    risk_level: TamperSeverity
    response_locked: bool
    human_review_required: bool
    execution_allowed: bool = False


def safety_invariants_hold() -> bool:
    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )


def _severity_rank(severity: TamperSeverity) -> int:
    return {
        TamperSeverity.LOW: 1,
        TamperSeverity.MEDIUM: 2,
        TamperSeverity.HIGH: 3,
        TamperSeverity.CRITICAL: 4,
    }[severity]


def _highest_severity(
    findings: tuple[TamperFinding, ...],
) -> TamperSeverity:
    if not findings:
        return TamperSeverity.LOW

    return max(
        (finding.severity for finding in findings),
        key=_severity_rank,
    )


def file_digest(path: Path) -> str:
    """Calculate deterministic SHA-256 for a file."""
    digest = sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def compare_file_digest(
    path: Path,
    expected_digest: str,
) -> TamperFinding | None:
    path = Path(path)

    if not path.exists():
        return TamperFinding(
            signal=TamperSignal.FILE_INTEGRITY_DRIFT,
            severity=TamperSeverity.CRITICAL,
            target=str(path),
            reason="expected file is missing",
            evidence={
                "expected_digest": expected_digest,
                "actual_digest": None,
            },
        )

    actual_digest = file_digest(path)

    if actual_digest == expected_digest:
        return None

    return TamperFinding(
        signal=TamperSignal.FILE_INTEGRITY_DRIFT,
        severity=TamperSeverity.HIGH,
        target=str(path),
        reason="file digest differs from trusted baseline",
        evidence={
            "expected_digest": expected_digest,
            "actual_digest": actual_digest,
        },
    )


def build_file_baseline(
    paths: tuple[Path, ...],
) -> dict[str, str]:
    baseline: dict[str, str] = {}

    for path in sorted(
        (Path(item) for item in paths),
        key=lambda item: str(item),
    ):
        if path.is_file():
            baseline[str(path)] = file_digest(path)

    return baseline


def detect_file_integrity_drift(
    baseline: Mapping[str, str],
) -> tuple[TamperFinding, ...]:
    findings: list[TamperFinding] = []

    for raw_path, expected_digest in sorted(
        baseline.items(),
    ):
        finding = compare_file_digest(
            Path(raw_path),
            expected_digest,
        )

        if finding is not None:
            findings.append(finding)

    return tuple(findings)


def detect_safety_state(
    state: Mapping[str, Any],
) -> TamperFinding | None:
    required = {
        "READ_ONLY": True,
        "DRY_RUN": True,
        "REAL_EXECUTION_BLOCKED": True,
        "HUMAN_REVIEW_REQUIRED": True,
        "RESPONSE_LOCKED": True,
    }

    mismatches = {
        key: {
            "expected": expected,
            "actual": state.get(key),
        }
        for key, expected in required.items()
        if state.get(key) is not expected
    }

    if not mismatches:
        return None

    return TamperFinding(
        signal=TamperSignal.SAFETY_STATE_DRIFT,
        severity=TamperSeverity.CRITICAL,
        target="guardian_hunter_safety_state",
        reason="one or more mandatory safety invariants differ",
        evidence={"mismatches": mismatches},
    )


def detect_authorization_anomaly(
    *,
    authorized: bool,
    execution_allowed: bool,
    human_review_required: bool,
) -> TamperFinding | None:
    if execution_allowed:
        return TamperFinding(
            signal=TamperSignal.AUTHORIZATION_ANOMALY,
            severity=TamperSeverity.CRITICAL,
            target="authorization",
            reason="execution gate unexpectedly enabled",
            evidence={
                "authorized": authorized,
                "execution_allowed": execution_allowed,
                "human_review_required": human_review_required,
            },
        )

    if not authorized and human_review_required is not True:
        return TamperFinding(
            signal=TamperSignal.AUTHORIZATION_ANOMALY,
            severity=TamperSeverity.HIGH,
            target="authorization",
            reason="unauthorized state lacks mandatory review",
            evidence={
                "authorized": authorized,
                "execution_allowed": execution_allowed,
                "human_review_required": human_review_required,
            },
        )

    return None


def detect_evidence_chain_anomaly(
    *,
    valid: bool,
    records: int,
    invalid_hash: bool,
    invalid_chain: bool,
) -> TamperFinding | None:
    if valid and not invalid_hash and not invalid_chain:
        return None

    return TamperFinding(
        signal=TamperSignal.EVIDENCE_CHAIN_ANOMALY,
        severity=TamperSeverity.CRITICAL,
        target="evidence_chain",
        reason="evidence integrity verification failed",
        evidence={
            "valid": valid,
            "records": records,
            "invalid_hash": invalid_hash,
            "invalid_chain": invalid_chain,
        },
    )


def detect_repeated_failures(
    *,
    failure_count: int,
    threshold: int = 3,
) -> TamperFinding | None:
    if threshold < 1:
        raise ValueError("threshold must be positive")

    if failure_count < threshold:
        return None

    severity = (
        TamperSeverity.CRITICAL
        if failure_count >= threshold * 2
        else TamperSeverity.HIGH
    )

    return TamperFinding(
        signal=TamperSignal.REPEATED_FAILURES,
        severity=severity,
        target="incident_transitions",
        reason="repeated failed transitions detected",
        evidence={
            "failure_count": failure_count,
            "threshold": threshold,
        },
    )


def detect_configuration_drift(
    *,
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
) -> TamperFinding | None:
    keys = set(expected) | set(actual)

    differences = {
        key: {
            "expected": expected.get(key),
            "actual": actual.get(key),
        }
        for key in sorted(keys)
        if expected.get(key) != actual.get(key)
    }

    if not differences:
        return None

    return TamperFinding(
        signal=TamperSignal.CONFIGURATION_DRIFT,
        severity=TamperSeverity.HIGH,
        target="guardian_hunter_configuration",
        reason="configuration differs from trusted baseline",
        evidence={"differences": differences},
    )


def assess_tamper(
    *,
    target: str,
    findings: tuple[TamperFinding, ...],
) -> TamperAssessment:
    if not safety_invariants_hold():
        raise RuntimeError("SAFETY_INVARIANTS_FAILED")

    return TamperAssessment(
        target=target,
        findings=findings,
        risk_level=_highest_severity(findings),
        response_locked=True,
        human_review_required=True,
        execution_allowed=False,
    )


def fail_closed(
    assessment: TamperAssessment,
) -> bool:
    return (
        assessment.execution_allowed is False
        and assessment.response_locked is True
        and assessment.human_review_required is True
        and READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and RESPONSE_LOCKED is True
    )


def finding_to_dict(
    finding: TamperFinding,
) -> dict[str, Any]:
    return {
        "signal": finding.signal.value,
        "severity": finding.severity.value,
        "target": finding.target,
        "reason": finding.reason,
        "evidence": dict(finding.evidence),
        "execution_allowed": finding.execution_allowed,
    }


def assessment_to_dict(
    assessment: TamperAssessment,
) -> dict[str, Any]:
    return {
        "target": assessment.target,
        "findings": [
            finding_to_dict(finding)
            for finding in assessment.findings
        ],
        "risk_level": assessment.risk_level.value,
        "response_locked": assessment.response_locked,
        "human_review_required": assessment.human_review_required,
        "execution_allowed": assessment.execution_allowed,
    }


def serialize_assessment(
    assessment: TamperAssessment,
) -> str:
    return json.dumps(
        assessment_to_dict(assessment),
        sort_keys=True,
        ensure_ascii=False,
    )
