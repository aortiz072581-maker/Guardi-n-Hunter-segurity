"""Phase 43 — Defensive Security Case Management.

Case organization, evidence references and investigation state.
No system, process or network mutation is performed.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


VALID_STATES = frozenset(
    {
        "OPEN",
        "INVESTIGATING",
        "REVIEW",
        "RECOVERY_REVIEW",
        "CLOSED",
    }
)


@dataclass
class SecurityCase:
    case_id: str
    title: str
    severity: str = "UNKNOWN"
    state: str = "OPEN"
    asset: str = "unknown"
    evidence_ids: List[str] = field(default_factory=list)
    alert_ids: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    mode: str = "READ_ONLY"
    execution_allowed: bool = False


def create_case(
    case_id: str,
    title: str,
    *,
    severity: str = "UNKNOWN",
    asset: str = "unknown",
) -> SecurityCase:
    case = SecurityCase(
        case_id=str(case_id),
        title=str(title),
        severity=str(severity),
        asset=str(asset),
    )

    case.history.append(
        {
            "event": "CASE_CREATED",
            "state": "OPEN",
            "mode": "READ_ONLY",
            "execution_allowed": False,
        }
    )

    return case


def transition_case(
    case: SecurityCase,
    new_state: str,
    *,
    reason: str = "",
) -> SecurityCase:
    state = str(new_state).upper()

    if state not in VALID_STATES:
        raise ValueError(f"Invalid case state: {state}")

    case.state = state
    case.history.append(
        {
            "event": "STATE_CHANGED",
            "state": state,
            "reason": str(reason),
            "mode": "READ_ONLY",
            "execution_allowed": False,
        }
    )

    return case


def attach_evidence(
    case: SecurityCase,
    evidence_ids: Iterable[str],
) -> SecurityCase:
    for evidence_id in evidence_ids:
        value = str(evidence_id)
        if value not in case.evidence_ids:
            case.evidence_ids.append(value)

    return case


def attach_alerts(
    case: SecurityCase,
    alert_ids: Iterable[str],
) -> SecurityCase:
    for alert_id in alert_ids:
        value = str(alert_id)
        if value not in case.alert_ids:
            case.alert_ids.append(value)

    return case


def validate_case(case: SecurityCase) -> bool:
    return (
        bool(case.case_id)
        and bool(case.title)
        and case.state in VALID_STATES
        and case.mode == "READ_ONLY"
        and case.execution_allowed is False
    )


def build_case_record(case: SecurityCase) -> Dict[str, Any]:
    return {
        "phase": 43,
        "component": "SECURITY_CASE_MANAGEMENT",
        "case_id": case.case_id,
        "title": case.title,
        "severity": case.severity,
        "state": case.state,
        "asset": case.asset,
        "evidence_ids": list(case.evidence_ids),
        "alert_ids": list(case.alert_ids),
        "history": [dict(item) for item in case.history],
        "mode": "READ_ONLY",
        "execution_allowed": False,
    }
