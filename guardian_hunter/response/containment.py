"""Guardian Hunter - containment planner.

Phase 18 starts with safe, non-destructive containment planning.
No firewall, interface-down, process-kill, or route-changing command
is executed by this module.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_containment_plan(
    incident_id: str,
    response: str,
    target: str,
    reason: str,
) -> dict:
    return {
        "action_id": f"GH-ACT-{uuid4().hex[:12]}",
        "incident_id": incident_id,
        "created_at": _utc_now(),
        "target": target,
        "reason": reason,
        "response": response,
        "mode": "DRY_RUN",
        "status": "PLANNED",
        "reversible": True,
        "executed": False,
    }


def verify_plan(plan: dict) -> dict:
    required = (
        "action_id",
        "incident_id",
        "target",
        "response",
        "mode",
        "status",
    )

    valid = all(key in plan for key in required)

    return {
        "verified": valid,
        "action_id": plan.get("action_id"),
        "status": "VERIFIED" if valid else "INVALID",
    }


def rollback_plan(plan: dict) -> dict:
    return {
        "action_id": plan.get("action_id"),
        "rollback_available": bool(plan.get("reversible")),
        "rollback_mode": "DRY_RUN",
        "status": "ROLLBACK_READY",
    }
