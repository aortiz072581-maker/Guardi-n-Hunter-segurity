"""Consolidated Guardian Hunter defensive observation flow.

Hardware -> Network -> Correlation -> Diagnosis -> Integrity/Tamper
-> Evidence-ready consolidated result.

No response action or real execution is permitted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from guardian_hunter.diagnosis.engine import (
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)
from guardian_hunter.integration.integrity_tamper import (
    inspect_integrity_tamper,
)
from guardian_hunter.integration.passive_host_observation import (
    observe_host,
)

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


def run_consolidated_defensive_flow(
    *,
    root: Path,
    baseline_file: Path,
    previous_hardware: dict | None = None,
    previous_network: dict | None = None,
    hardware: dict | None = None,
    network: dict | None = None,
) -> dict[str, Any]:
    """Run the local defensive chain while remaining fail-closed."""

    observation = observe_host(
        previous_hardware,
        previous_network,
        hardware=hardware,
        network=network,
    )

    correlation = observation.get("correlation", {}) or {}

    categories = correlation.get("categories", [])
    if not isinstance(categories, list):
        categories = []

    score = float(
        correlation.get(
            "correlated_score",
            correlation.get("score", 0.0),
        )
        or 0.0
    )

    diagnosis = diagnose_problem({
        "categories": categories,
        "correlated_score": score,
    })

    if not validate_diagnosis(diagnosis):
        raise RuntimeError("DIAGNOSIS_INVARIANT_FAILED")

    protection = inspect_integrity_tamper(
        baseline_file,
        root,
    )

    return {
        "status": "review_required",
        "hardware": observation["hardware"],
        "network": observation["network"],
        "hardware_changes": observation["hardware_changes"],
        "network_changes": observation["network_changes"],
        "correlation": correlation,
        "diagnosis": diagnosis_to_dict(diagnosis),
        "integrity_tamper": protection,
        "evidence": {
            "hardware_observed": True,
            "network_observed": True,
            "correlation_completed": True,
            "diagnosis_completed": True,
            "integrity_checked": True,
            "tamper_checked": True,
        },
        "read_only": True,
        "dry_run": True,
        "real_execution_blocked": True,
        "human_review_required": True,
        "response_locked": True,
        "execution_allowed": False,
    }


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "RESPONSE_LOCKED",
    "run_consolidated_defensive_flow",
]
