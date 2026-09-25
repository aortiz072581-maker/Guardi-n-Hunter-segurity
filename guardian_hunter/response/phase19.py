from datetime import datetime, timezone
from uuid import uuid4


ALLOWED_ACTIONS = {
    "ISOLATE_NETWORK",
    "QUARANTINE_ASSET",
    "STOP_AUTOMATION",
    "ESCALATE",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_plan(
    incident_id: str,
    target: str,
    action: str,
    reason: str,
) -> dict:
    if not incident_id:
        raise ValueError("incident_id required")

    if not target:
        raise ValueError("target required")

    if action not in ALLOWED_ACTIONS:
        raise ValueError("unsupported response action")

    return {
        "action_id": f"GH-R19-{uuid4().hex[:12]}",
        "incident_id": incident_id,
        "target": target,
        "action": action,
        "reason": reason,
        "created_at": utc_now(),

        # Safety defaults
        "mode": "DRY_RUN",
        "status": "PLANNED",
        "approved": False,
        "execution_gate": False,
        "executed": False,
        "reversible": True,
    }


def verify_plan(plan: dict) -> dict:
    required = (
        "action_id",
        "incident_id",
        "target",
        "action",
        "mode",
        "status",
        "execution_gate",
        "executed",
    )

    valid = all(key in plan for key in required)

    if plan.get("action") not in ALLOWED_ACTIONS:
        valid = False

    if plan.get("mode") != "DRY_RUN":
        valid = False

    if plan.get("executed") is True:
        valid = False

    return {
        "verified": valid,
        "action_id": plan.get("action_id"),
        "status": "VERIFIED" if valid else "INVALID",
    }


def approve_plan(plan: dict, approver: str) -> dict:
    if not approver:
        raise ValueError("approver required")

    verified = verify_plan(plan)

    if not verified["verified"]:
        raise ValueError("plan verification failed")

    approved = dict(plan)
    approved["approved"] = True
    approved["approved_by"] = approver
    approved["approved_at"] = utc_now()

    # Phase 19 never opens execution automatically.
    approved["execution_gate"] = False
    approved["status"] = "APPROVED_PENDING_EXECUTION"

    return approved


def rollback_plan(plan: dict) -> dict:
    return {
        "action_id": plan.get("action_id"),
        "rollback_available": bool(plan.get("reversible")),
        "rollback_mode": "DRY_RUN",
        "status": "ROLLBACK_READY",
    }
