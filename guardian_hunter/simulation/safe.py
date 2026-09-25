"""Phase 33 — End-to-end defensive simulation.

Simulation only. No system/network/process changes are performed.
"""

from datetime import datetime, timezone

from guardian_hunter.audit.trail import (
    create_event,
    append_event,
    verify_trail,
)

from guardian_hunter.policy.guard import (
    evaluate_policy,
)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def simulate_incident(
    *,
    incident_id="SIM-001",
    risk_score=75,
    action="CONTAINMENT_REVIEW",
):
    """Simulate the defensive decision chain without execution."""

    trail = []

    event = create_event(
        event_type="INCIDENT_DETECTED",
        source="SIMULATION",
        severity="HIGH" if risk_score >= 60 else "MEDIUM",
        details={
            "incident_id": incident_id,
            "risk_score": risk_score,
        },
    )
    append_event(trail, event)

    policy = evaluate_policy(
        action=action,
        mode="SIMULATION",
        approved=False,
        execution_requested=False,
    )

    event = create_event(
        event_type="POLICY_EVALUATED",
        source="POLICY_GUARD",
        severity="INFO",
        details=policy,
        previous_hash=trail[-1]["hash"],
    )
    append_event(trail, event)

    event = create_event(
        event_type="RESPONSE_SIMULATED",
        source="SAFE_SIMULATION",
        severity="INFO",
        details={
            "incident_id": incident_id,
            "action": action,
            "executed": False,
            "execution_allowed": False,
        },
        previous_hash=trail[-1]["hash"],
    )
    append_event(trail, event)

    integrity = verify_trail(trail)

    return {
        "simulation": "GUARDIAN_HUNTER_SAFE",
        "generated_at": _utc_now(),
        "incident_id": incident_id,
        "risk_score": risk_score,
        "policy": policy,
        "audit": trail,
        "audit_integrity": integrity,
        "executed": False,
        "execution_allowed": False,
        "mode": "SIMULATION",
    }


def verify_simulation(result):
    """Verify simulation safety invariants."""
    policy = result.get("policy", {})
    integrity = result.get("audit_integrity", {})

    valid = (
        result.get("simulation") == "GUARDIAN_HUNTER_SAFE"
        and result.get("mode") == "SIMULATION"
        and result.get("executed") is False
        and result.get("execution_allowed") is False
        and policy.get("execution_allowed") is False
        and integrity.get("valid") is True
    )

    return {
        "valid": valid,
        "executed": False,
        "execution_allowed": False,
        "audit_valid": integrity.get("valid") is True,
    }
