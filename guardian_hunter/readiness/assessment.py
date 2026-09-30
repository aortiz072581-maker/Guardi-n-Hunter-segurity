"""Phase 45 — Defensive Readiness Assessment.

Evaluates whether security controls are prepared for defensive
incident handling. This is an assessment only; no real action is taken.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


REQUIRED_CONTROLS = (
    "policy_guard",
    "audit_integrity",
    "evidence_integrity",
    "baseline_integrity",
    "health_monitor",
    "response_lock",
)


@dataclass(frozen=True)
class ReadinessResult:
    readiness: str
    score: float
    passed_controls: int
    failed_controls: int
    total_controls: int
    gaps: List[str]
    mode: str
    execution_allowed: bool


def assess_readiness(
    controls: Dict[str, bool],
) -> ReadinessResult:
    gaps = []

    for control in REQUIRED_CONTROLS:
        if controls.get(control) is not True:
            gaps.append(control)

    total = len(REQUIRED_CONTROLS)
    passed = total - len(gaps)
    score = (passed / total * 100.0) if total else 100.0

    if not gaps:
        readiness = "READY"
    elif score >= 70:
        readiness = "REVIEW_REQUIRED"
    else:
        readiness = "DEGRADED"

    return ReadinessResult(
        readiness=readiness,
        score=score,
        passed_controls=passed,
        failed_controls=len(gaps),
        total_controls=total,
        gaps=gaps,
        mode="READ_ONLY",
        execution_allowed=False,
    )


def readiness_gate(result: ReadinessResult) -> bool:
    """Safety gate for readiness assessment.

    Readiness never authorizes real execution.
    """
    return False


def build_readiness_report(
    result: ReadinessResult,
) -> Dict[str, Any]:
    return {
        "phase": 45,
        "component": "DEFENSIVE_READINESS",
        "readiness": result.readiness,
        "score": result.score,
        "passed_controls": result.passed_controls,
        "failed_controls": result.failed_controls,
        "total_controls": result.total_controls,
        "gaps": list(result.gaps),
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }


def validate_readiness_contract(
    result: ReadinessResult,
) -> bool:
    return (
        result.mode == "READ_ONLY"
        and result.execution_allowed is False
        and 0.0 <= result.score <= 100.0
        and result.passed_controls + result.failed_controls
        == result.total_controls
    )


def build_readiness_summary(
    results: Iterable[ReadinessResult],
) -> Dict[str, Any]:
    items = list(results)

    if not items:
        return {
            "assessments": 0,
            "average_score": 0.0,
            "mode": "READ_ONLY",
            "execution_allowed": False,
        }

    average = sum(item.score for item in items) / len(items)

    return {
        "assessments": len(items),
        "average_score": average,
        "readiness_states": [item.readiness for item in items],
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
