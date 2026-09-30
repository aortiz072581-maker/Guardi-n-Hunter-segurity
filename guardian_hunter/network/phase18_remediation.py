"""Phase 18.17 — Defensive Remediation Plan.

READ_ONLY / DRY_RUN only.
No network, firewall, process, routing or system mutation.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class NetworkRemediationPlan:
    risk_level: str
    risk_score: float
    actions: List[str]
    priority: str
    execution_allowed: bool
    mode: str
    status: str


def _priority(risk_level: str) -> str:
    level = str(risk_level).upper()
    if level == "CRITICAL":
        return "IMMEDIATE_REVIEW"
    if level == "HIGH":
        return "HIGH_REVIEW"
    if level == "WATCH":
        return "ENHANCED_REVIEW"
    return "ROUTINE_REVIEW"


def _actions(risk_level: str) -> List[str]:
    level = str(risk_level).upper()

    if level == "CRITICAL":
        return [
            "COLLECT_NETWORK_EVIDENCE",
            "VERIFY_BASELINE_INTEGRITY",
            "REVIEW_DNS_AND_LISTENERS",
            "REVIEW_CONNECTIONS_AND_EGRESS",
            "ESCALATE_FOR_HUMAN_REVIEW",
        ]

    if level == "HIGH":
        return [
            "COLLECT_NETWORK_EVIDENCE",
            "VERIFY_BASELINE_INTEGRITY",
            "REVIEW_NETWORK_CHANGES",
            "ENHANCED_MONITORING",
        ]

    if level == "WATCH":
        return [
            "COLLECT_SUPPORTING_EVIDENCE",
            "COMPARE_WITH_BASELINE",
            "ENHANCED_MONITORING",
        ]

    return [
        "CONTINUE_MONITORING",
        "MAINTAIN_BASELINE",
    ]


def build_network_remediation_plan(
    risk_level: str,
    risk_score: float,
) -> NetworkRemediationPlan:
    return NetworkRemediationPlan(
        risk_level=str(risk_level).upper(),
        risk_score=float(risk_score),
        actions=_actions(risk_level),
        priority=_priority(risk_level),
        execution_allowed=False,
        mode="READ_ONLY",
        status="PLANNED_ONLY",
    )


def remediation_to_dict(
    plan: NetworkRemediationPlan,
) -> Dict[str, Any]:
    return asdict(plan)


def validate_network_remediation_plan(
    plan: NetworkRemediationPlan,
) -> bool:
    return (
        isinstance(plan, NetworkRemediationPlan)
        and plan.execution_allowed is False
        and plan.mode == "READ_ONLY"
        and plan.status == "PLANNED_ONLY"
        and 0 <= plan.risk_score <= 100
        and bool(plan.actions)
    )
