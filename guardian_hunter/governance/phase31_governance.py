"""Phase 31 — Defensive Security Governance."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass
class SecurityGovernance:
    controls: List[str]
    control_count: int
    all_controls_present: bool
    response_locked: bool
    mode: str
    execution_allowed: bool
    status: str


REQUIRED_CONTROLS = [
    "READ_ONLY",
    "DRY_RUN",
    "EXECUTION_BLOCK",
    "AUDIT_TRAIL",
    "EVIDENCE_INTEGRITY",
    "RESPONSE_LOCK",
]


def build_security_governance() -> SecurityGovernance:
    controls = list(REQUIRED_CONTROLS)

    return SecurityGovernance(
        controls=controls,
        control_count=len(controls),
        all_controls_present=True,
        response_locked=True,
        mode="READ_ONLY",
        execution_allowed=False,
        status="GOVERNANCE_ENFORCED",
    )


def governance_to_dict(
    governance: SecurityGovernance,
) -> Dict[str, Any]:
    return asdict(governance)


def validate_security_governance(
    governance: SecurityGovernance,
) -> bool:
    return (
        isinstance(governance, SecurityGovernance)
        and governance.control_count == len(governance.controls)
        and governance.all_controls_present is True
        and governance.response_locked is True
        and governance.mode == "READ_ONLY"
        and governance.execution_allowed is False
        and governance.status == "GOVERNANCE_ENFORCED"
    )
