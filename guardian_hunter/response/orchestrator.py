"""Guardian Hunter - Phase 18 response orchestrator.

Connects risk/policy/containment decisions while keeping
response execution disabled by default.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from guardian_hunter.response.policy import build_policy_decision
from guardian_hunter.response.containment import (
    create_containment_plan,
    rollback_plan,
    verify_plan,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_incident(
    risk_level: str,
    reason: str,
    target: str,
    authorized: bool = False,
    risk_data: dict | None = None,
) -> dict:
    """Create a complete defensive response decision."""

    incident_id = f"GH-INC-{uuid4().hex[:12]}"

    policy = build_policy_decision(
        risk_level=risk_level,
        reason=reason,
        authorized=authorized,
    )

    plan = create_containment_plan(
        incident_id=incident_id,
        response=policy["response"],
        target=target,
        reason=reason,
    )

    verification = verify_plan(plan)
    rollback = rollback_plan(plan)

    return {
        "incident_id": incident_id,
        "created_at": _utc_now(),
        "risk": risk_data or {
            "level": risk_level,
        },
        "target": target,
        "reason": reason,
        "authorization": {
            "authorized": bool(authorized),
        },
        "policy": policy,
        "containment": plan,
        "verification": verification,
        "rollback": rollback,
    }


def response_summary(incident: dict) -> dict:
    """Return a compact audit-friendly summary."""

    return {
        "incident_id": incident.get("incident_id"),
        "risk_level": incident.get("risk", {}).get("level"),
        "target": incident.get("target"),
        "response": incident.get("policy", {}).get("response"),
        "authorized": incident.get("authorization", {}).get(
            "authorized", False
        ),
        "execution_allowed": incident.get(
            "policy", {}
        ).get("execution_allowed", False),
        "containment_status": incident.get(
            "containment", {}
        ).get("status"),
        "verification": incident.get(
            "verification", {}
        ).get("status"),
        "rollback": incident.get(
            "rollback", {}
        ).get("status"),
    }
