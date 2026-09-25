"""Phase 25 — Defensive Response Orchestrator 2.0.

Execution remains disabled by default. This module prepares and verifies
response workflows without performing destructive actions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_response_workflow(
    incident_id: str,
    decision: dict[str, Any] | None = None,
    *,
    mode: str = "DRY_RUN",
) -> dict[str, Any]:
    decision = dict(decision or {})

    return {
        "incident_id": incident_id,
        "created_at": utc_now(),
        "state": "PLANNED",
        "mode": "DRY_RUN",
        "execution_allowed": False,
        "requires_approval": bool(
            decision.get("requires_approval", False)
        ),
        "rollback_available": True,
        "verified": False,
        "steps": [
            {
                "name": "prepare",
                "status": "READY",
            },
            {
                "name": "approval",
                "status": (
                    "REQUIRED"
                    if decision.get("requires_approval", False)
                    else "NOT_REQUIRED"
                ),
            },
            {
                "name": "execution",
                "status": "BLOCKED",
            },
            {
                "name": "verification",
                "status": "PENDING",
            },
            {
                "name": "rollback",
                "status": "AVAILABLE",
            },
        ],
    }


def approve_workflow(
    workflow: dict[str, Any],
    approved: bool = False,
) -> dict[str, Any]:
    result = dict(workflow)

    if approved:
        result["approval"] = {
            "approved": True,
            "approved_at": utc_now(),
        }
        result["state"] = "APPROVED"

        # Approval alone never unlocks real execution.
        result["execution_allowed"] = False
    else:
        result["approval"] = {
            "approved": False,
            "approved_at": None,
        }
        result["state"] = "REJECTED"
        result["execution_allowed"] = False

    return result


def verify_workflow(
    workflow: dict[str, Any],
) -> dict[str, Any]:
    result = dict(workflow)

    result["verified"] = True
    result["verification"] = {
        "verified": True,
        "verified_at": utc_now(),
        "execution_observed": False,
    }

    return result


def rollback_workflow(
    workflow: dict[str, Any],
) -> dict[str, Any]:
    result = dict(workflow)

    result["state"] = "ROLLED_BACK"
    result["execution_allowed"] = False
    result["rollback"] = {
        "available": True,
        "performed": True,
        "performed_at": utc_now(),
    }

    return result
