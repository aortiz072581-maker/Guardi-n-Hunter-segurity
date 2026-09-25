"""Phase 42 — Defensive Response Governance.

Authorization and traceability layer.
This phase never unlocks real execution.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


BLOCKED_ACTIONS = frozenset(
    {
        "DELETE",
        "WIPE",
        "DESTROY",
        "PERSIST",
        "CREDENTIAL_CHANGE",
        "UNAUTHORIZED_EXECUTION",
    }
)

ALLOWED_MODES = frozenset(
    {
        "READ_ONLY",
        "DRY_RUN",
        "SIMULATION",
    }
)


@dataclass(frozen=True)
class GovernanceDecision:
    action: str
    mode: str
    policy_status: str
    approval_required: bool
    approved: bool
    traceable: bool
    execution_allowed: bool
    reason: str


def evaluate_governance(
    *,
    action: str,
    mode: str = "DRY_RUN",
    approved: bool = False,
    traceable: bool = True,
) -> GovernanceDecision:
    normalized_action = str(action).upper()
    normalized_mode = str(mode).upper()

    if normalized_mode not in ALLOWED_MODES:
        return GovernanceDecision(
            action=normalized_action,
            mode=normalized_mode,
            policy_status="BLOCKED",
            approval_required=True,
            approved=bool(approved),
            traceable=bool(traceable),
            execution_allowed=False,
            reason="Unsupported execution mode.",
        )

    if normalized_action in BLOCKED_ACTIONS:
        return GovernanceDecision(
            action=normalized_action,
            mode=normalized_mode,
            policy_status="BLOCKED",
            approval_required=True,
            approved=bool(approved),
            traceable=bool(traceable),
            execution_allowed=False,
            reason="Action is prohibited by defensive governance policy.",
        )

    if not traceable:
        return GovernanceDecision(
            action=normalized_action,
            mode=normalized_mode,
            policy_status="BLOCKED",
            approval_required=True,
            approved=bool(approved),
            traceable=False,
            execution_allowed=False,
            reason="Response must remain fully traceable.",
        )

    return GovernanceDecision(
        action=normalized_action,
        mode=normalized_mode,
        policy_status="REVIEW_ONLY",
        approval_required=True,
        approved=bool(approved),
        traceable=True,
        execution_allowed=False,
        reason="Governance review recorded; real execution remains locked.",
    )


def governance_gate(decision: GovernanceDecision) -> bool:
    """Final safety gate. It intentionally never returns True."""
    return False


def create_governance_record(
    decision: GovernanceDecision,
    *,
    incident_id: str = "",
    operator: str = "system",
) -> Dict[str, Any]:
    return {
        "phase": 42,
        "component": "RESPONSE_GOVERNANCE",
        "incident_id": str(incident_id),
        "operator": str(operator),
        "action": decision.action,
        "mode": decision.mode,
        "policy_status": decision.policy_status,
        "approval_required": decision.approval_required,
        "approved": decision.approved,
        "traceable": decision.traceable,
        "execution_allowed": False,
        "reason": decision.reason,
    }


def build_governance_chain(
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "phase": 42,
        "records": [dict(record) for record in records],
        "record_count": len(records),
        "mode": "DRY_RUN",
        "execution_allowed": False,
        "integrity": "TRACEABLE",
    }
