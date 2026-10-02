"""Consolidated Guardian Hunter defensive observation flow.

Hardware -> Network -> Correlation -> Diagnosis -> Integrity/Tamper
-> Evidence-ready consolidated result.

No response action or real execution is permitted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from guardian_hunter.correlation.phase19_correlation import (
    correlate_signals,
    correlation_to_dict,
    validate_signal_correlation,
)

from guardian_hunter.diagnosis.engine import (
    diagnose_problem,
    diagnosis_to_dict,
    validate_diagnosis,
)
from guardian_hunter.integration.problem_advisor import analyze_problem
from guardian_hunter.incident.state import (
    IncidentState,
    create_incident,
    transition_incident,
    plan_recovery,
    request_recovery_review,
    incident_to_dict,
    transition_to_dict,
    fail_closed as incident_fail_closed,
)
from guardian_hunter.evidence.incident import (
    create_incident_record,
    verify_incident_record,
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

    categories = list(categories)
    signals = correlation.get("signals", []) or []

    if any(
        signal in {"HARDWARE_CHANGED", "NEW_HARDWARE"}
        for signal in signals
    ):
        if "hardware" not in categories:
            categories.append("hardware")

    if any(
        signal in {
            "NETWORK_INTERFACE_CHANGED",
            "ROUTE_CHANGED",
            "NEIGHBOR_TABLE_CHANGED",
            "ADDRESS_CHANGED",
        }
        for signal in signals
    ):
        if "network" not in categories:
            categories.append("network")

    score = float(
        correlation.get(
            "correlated_score",
            correlation.get("score", 0.0),
        )
        or 0.0
    )

    if score == 0.0:
        score = {
            "low": 25.0,
            "medium": 50.0,
            "high": 70.0,
        }.get(
            str(correlation.get("risk_hint", "normal")).lower(),
            0.0,
        )

    protection = inspect_integrity_tamper(
        baseline_file,
        root,
    )

    integrity_changed = bool(
        protection.get("added")
        or protection.get("modified")
        or protection.get("deleted")
    )

    if integrity_changed:
        categories = list(categories)
        if "integrity" not in categories:
            categories.append("integrity")
        score = max(score, 70.0)

    phase19_signals = [
        {
            "signal_id": x,
            "category": (
                "hardware"
                if x in {"HARDWARE_CHANGED", "NEW_HARDWARE"}
                else "network"
            ),
            "score": score,
        }
        for x in signals
    ]

    if integrity_changed:
        phase19_signals.append({
            "signal_id": "INTEGRITY_CHANGE",
            "category": "integrity",
            "score": 70.0,
        })

    phase19 = correlate_signals(phase19_signals)

    if not validate_signal_correlation(phase19):
        raise RuntimeError("CORRELATION_INVARIANT_FAILED")

    categories = list(phase19.categories)
    score = phase19.correlated_score

    diagnosis = diagnose_problem({
        "categories": categories,
        "correlated_score": score,
    })

    if not validate_diagnosis(diagnosis):
        raise RuntimeError("DIAGNOSIS_INVARIANT_FAILED")

    problem_advice = [
        analyze_problem(
            "integrity_tamper" if c == "integrity" else c,
            False,
        )
        for c in categories
        if c in {"hardware", "network", "integrity"}
    ]

    incident_record = create_incident_record(
        incident_id="consolidated-defensive-flow",
        decision=diagnosis_to_dict(diagnosis),
        correlation=correlation_to_dict(phase19),
        evidence=[{"problem_advice": problem_advice}],
    )

    incident_verified = verify_incident_record(incident_record)

    if not incident_verified:
        raise RuntimeError("INCIDENT_EVIDENCE_INTEGRITY_FAILED")

    incident = create_incident(
        incident_id="consolidated-defensive-flow",
        risk_level=diagnosis.risk_level,
        target="local-defensive-host",
        reason="consolidated defensive analysis",
    )

    incident, _ = transition_incident(
        incident,
        IncidentState.TRIAGED,
        reason="defensive triage completed",
    )
    incident, _ = transition_incident(
        incident,
        IncidentState.AUTHORIZED,
        reason="recovery planning authorized for review only",
    )

    incident, recovery_plan = plan_recovery(
        incident,
        reason="prepare recovery plan only",
    )

    incident, recovery_review = request_recovery_review(
        incident,
        reason="human recovery review required",
    )

    if not incident_fail_closed(incident):
        raise RuntimeError("INCIDENT_FAIL_CLOSED_FAILED")

    return {
        "status": (
            "blocked"
            if integrity_changed
            else "review_required"
        ),
        "hardware": observation["hardware"],
        "network": observation["network"],
        "hardware_changes": observation["hardware_changes"],
        "network_changes": observation["network_changes"],
        "correlation": correlation,
        "diagnosis": diagnosis_to_dict(diagnosis),
        "problem_advice": problem_advice,
        "recovery": {
            "incident": incident_to_dict(incident),
            "plan": transition_to_dict(recovery_plan),
            "review": transition_to_dict(recovery_review),
            "automatic_recovery": False,
            "execution_allowed": False,
            "response_locked": True,
        },
        "integrity_tamper": protection,
        "phase19_correlation": correlation_to_dict(phase19),
        "defensive_summary": {
            "incident_priority": diagnosis.risk_level,
            "recommended_actions": list(diagnosis.recommendations),
            "signal_count": len(signals) + (1 if integrity_changed else 0),
            "categories": sorted(set(categories)),
            "active_defenses": sorted(set(categories)),
            "multi_signal": len(set(categories)) > 1,
            "block_reason": (
                "PROTECTED_FILE_INTEGRITY_CHANGE"
                if integrity_changed
                else None
            ),
            "execution_allowed": False,
            "response_locked": True,
        },
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
