"""Phase 21 — Defensive Response Orchestrator.

Planning and sequencing only.
No real response execution.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class DefensiveResponsePlan:
    risk_level: str
    decision: str
    steps: List[str]
    step_count: int
    response_locked: bool
    dry_run: bool
    status: str
    mode: str
    execution_allowed: bool


def build_response_plan(
    risk_level: str,
    decision: str,
    collect_evidence: bool = True,
) -> DefensiveResponsePlan:

    steps: List[str] = [
        "VALIDATE_INTEGRITY",
        "RECORD_SECURITY_EVENT",
    ]

    if collect_evidence:
        steps.append("COLLECT_READ_ONLY_EVIDENCE")

    level = str(risk_level).upper()

    if level in {"HIGH", "CRITICAL"}:
        steps.append("ENHANCED_MONITORING")

    if level == "CRITICAL":
        steps.append("ESCALATE_FOR_HUMAN_REVIEW")

    steps.append("KEEP_RESPONSE_LOCKED")

    return DefensiveResponsePlan(
        risk_level=level,
        decision=str(decision),
        steps=steps,
        step_count=len(steps),
        response_locked=True,
        dry_run=True,
        status="RESPONSE_PLAN_ONLY",
        mode="READ_ONLY",
        execution_allowed=False,
    )


def response_plan_to_dict(
    plan: DefensiveResponsePlan,
) -> Dict[str, Any]:
    return asdict(plan)


def validate_response_plan(
    plan: DefensiveResponsePlan,
) -> bool:
    return (
        isinstance(plan, DefensiveResponsePlan)
        and plan.step_count == len(plan.steps)
        and plan.response_locked is True
        and plan.dry_run is True
        and plan.execution_allowed is False
        and plan.mode == "READ_ONLY"
        and plan.status == "RESPONSE_PLAN_ONLY"
        and bool(plan.steps)
    )
