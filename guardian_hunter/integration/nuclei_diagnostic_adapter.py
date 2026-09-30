"""Connect authorized Nuclei observations to Guardian Hunter defensive analysis.

Analysis and planning only.
This module never performs containment, remediation, or real execution.
"""

from __future__ import annotations

from typing import Any, Dict

from guardian_hunter.risk import calculate_risk
from guardian_hunter.diagnosis.engine import (
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)
from guardian_hunter.decision.phase20_decision import (
    build_defensive_decision,
    decision_to_dict,
    validate_defensive_decision,
)
from guardian_hunter.response.phase21_orchestrator import (
    build_response_plan,
    response_plan_to_dict,
    validate_response_plan,
)

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
RESPONSE_LOCKED = True


def analyze_nuclei_result(
    nuclei_result: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Risk-score, diagnose, decide and plan from an already collected result."""

    nuclei_result = nuclei_result if isinstance(nuclei_result, dict) else {}

    base = {
        "status": "blocked",
        "source": "nuclei",
        "authorized": bool(nuclei_result.get("authorized", False)),
        "findings": [],
        "risk": {},
        "diagnosis": None,
        "decision": None,
        "response_plan": None,
        "containment_recommended": False,
        "execution_allowed": False,
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "response_locked": True,
    }

    # Fail closed: unauthorized observations never become actionable.
    if not base["authorized"]:
        return base

    findings = nuclei_result.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    safe_findings = [
        finding
        for finding in findings
        if isinstance(finding, dict)
    ]

    risk = calculate_risk(safe_findings)
    score = float(risk.get("max_score", 0.0) or 0.0)

    correlation_view = {
        "categories": ["vulnerability"] if safe_findings else [],
        "correlated_score": score,
    }

    diagnosis = diagnose_problem(correlation_view)

    if not validate_diagnosis(diagnosis):
        raise RuntimeError("DIAGNOSIS_INVARIANT_FAILED")

    decision = build_defensive_decision(
        risk_level=diagnosis.risk_level,
        risk_score=diagnosis.risk_score,
    )

    if not validate_defensive_decision(decision):
        raise RuntimeError("DECISION_INVARIANT_FAILED")

    response_plan = build_response_plan(
        risk_level=decision.risk_level,
        decision=decision.decision,
        collect_evidence=decision.collect_evidence,
    )

    if not validate_response_plan(response_plan):
        raise RuntimeError("RESPONSE_PLAN_INVARIANT_FAILED")

    diagnosis_dict = diagnosis_to_dict(diagnosis)
    decision_dict = decision_to_dict(decision)
    response_plan_dict = response_plan_to_dict(response_plan)

    base.update(
        {
            "status": "review_required" if safe_findings else "ok",
            "findings": safe_findings,
            "risk": risk,
            "diagnosis": diagnosis_dict,
            "decision": decision_dict,
            "response_plan": response_plan_dict,

            # Recommendation only. No containment is executed.
            "containment_recommended": (
                diagnosis.risk_level in {"HIGH", "CRITICAL"}
            ),

            # Global safety invariants.
            "execution_allowed": False,
            "read_only": True,
            "dry_run": True,
            "real_execution_blocked": True,
            "response_locked": True,
        }
    )

    return base


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "RESPONSE_LOCKED",
    "analyze_nuclei_result",
]
