"""Guardian Hunter — diagnostic E2E defensive flow.

Adds read-only diagnosis to the existing defensive flow.
It never enables real execution.
"""

from __future__ import annotations

from typing import Any, Dict

from guardian_hunter.integration.e2e_defensive_flow import run_defensive_flow
from guardian_hunter.diagnosis.engine import (
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
RESPONSE_LOCKED = True


def run_diagnostic_defensive_flow(
    **kwargs: Any,
) -> Dict[str, Any]:

    result = run_defensive_flow(**kwargs)

    # Fail closed: preserve blocked/early-return states.
    if result.get("status") == "blocked":
        result["diagnosis"] = None
        return result

    risk = result.get("risk", {}) or {}

    score = float(
        risk.get(
            "max_score",
            risk.get("score", 0.0),
        )
        or 0.0
    )

    assessment = result.get("assessment", {}) or {}
    report = assessment.get("report", {}) or {}

    categories = report.get("categories", [])

    if not isinstance(categories, list):
        categories = []

    correlation_view = {
        "categories": categories,
        "correlated_score": score,
    }

    diagnosis = diagnose_problem(correlation_view)

    if not validate_diagnosis(diagnosis):
        raise RuntimeError("DIAGNOSIS_INVARIANT_FAILED")

    result["diagnosis"] = diagnosis_to_dict(diagnosis)

    # Reinforce global safety invariants.
    result["execution_allowed"] = False
    result["read_only"] = True
    result["dry_run"] = True
    result["real_execution_blocked"] = True
    result["response_locked"] = True

    return result


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "RESPONSE_LOCKED",
    "run_diagnostic_defensive_flow",
]
