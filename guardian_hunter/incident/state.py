"""
Guardian Hunter — Incident State & Recovery v1

State machine for defensive incident lifecycle management.

This module ONLY plans and records state transitions.
It does not execute containment, recovery, rollback, or system commands.

Safety invariants are fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


class IncidentState(str, Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    AUTHORIZED = "AUTHORIZED"
    CONTAINMENT_PLANNED = "CONTAINMENT_PLANNED"
    CONTAINMENT_REVIEW = "CONTAINMENT_REVIEW"
    RECOVERY_PLANNED = "RECOVERY_PLANNED"
    RECOVERY_REVIEW = "RECOVERY_REVIEW"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"
    LOCKED = "LOCKED"


class RecoveryAction(str, Enum):
    PLAN_ONLY = "PLAN_ONLY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RECOVERY_REVIEW = "RECOVERY_REVIEW"


@dataclass(frozen=True)
class Incident:
    incident_id: str
    state: IncidentState
    risk_level: str
    target: str
    reason: str
    evidence_ids: tuple[str, ...] = ()
    recovery_action: RecoveryAction = RecoveryAction.PLAN_ONLY
    execution_allowed: bool = False


@dataclass(frozen=True)
class Transition:
    incident_id: str
    previous_state: IncidentState
    new_state: IncidentState
    reason: str
    execution_allowed: bool
    human_review_required: bool
    dry_run: bool
    real_execution_blocked: bool
    response_locked: bool


_ALLOWED_TRANSITIONS: dict[IncidentState, frozenset[IncidentState]] = {
    IncidentState.NEW: frozenset({
        IncidentState.TRIAGED,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.TRIAGED: frozenset({
        IncidentState.AUTHORIZED,
        IncidentState.CONTAINMENT_REVIEW,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.AUTHORIZED: frozenset({
        IncidentState.CONTAINMENT_PLANNED,
        IncidentState.RECOVERY_PLANNED,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.CONTAINMENT_PLANNED: frozenset({
        IncidentState.CONTAINMENT_REVIEW,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.CONTAINMENT_REVIEW: frozenset({
        IncidentState.RECOVERY_PLANNED,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.RECOVERY_PLANNED: frozenset({
        IncidentState.RECOVERY_REVIEW,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.RECOVERY_REVIEW: frozenset({
        IncidentState.RESOLVED,
        IncidentState.LOCKED,
        IncidentState.FAILED,
    }),
    IncidentState.RESOLVED: frozenset(),
    IncidentState.FAILED: frozenset({
        IncidentState.LOCKED,
    }),
    IncidentState.LOCKED: frozenset(),
}


def safety_invariants_hold() -> bool:
    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )


def allowed_transitions(
    state: IncidentState,
) -> frozenset[IncidentState]:
    return _ALLOWED_TRANSITIONS.get(
        state,
        frozenset(),
    )


def can_transition(
    current: IncidentState,
    target: IncidentState,
) -> bool:
    if not safety_invariants_hold():
        return False

    return target in allowed_transitions(current)


def create_incident(
    *,
    incident_id: str,
    risk_level: str,
    target: str,
    reason: str,
    evidence_ids: tuple[str, ...] = (),
) -> Incident:
    if not safety_invariants_hold():
        raise RuntimeError("SAFETY_INVARIANTS_FAILED")

    return Incident(
        incident_id=incident_id,
        state=IncidentState.NEW,
        risk_level=risk_level,
        target=target,
        reason=reason,
        evidence_ids=evidence_ids,
        execution_allowed=False,
    )


def transition_incident(
    incident: Incident,
    target_state: IncidentState,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    if not safety_invariants_hold():
        raise RuntimeError("SAFETY_INVARIANTS_FAILED")

    if not can_transition(
        incident.state,
        target_state,
    ):
        raise ValueError(
            f"INVALID_TRANSITION:"
            f"{incident.state.value}->{target_state.value}"
        )

    transition = Transition(
        incident_id=incident.incident_id,
        previous_state=incident.state,
        new_state=target_state,
        reason=reason,
        execution_allowed=False,
        human_review_required=True,
        dry_run=True,
        real_execution_blocked=True,
        response_locked=True,
    )

    updated = Incident(
        incident_id=incident.incident_id,
        state=target_state,
        risk_level=incident.risk_level,
        target=incident.target,
        reason=incident.reason,
        evidence_ids=incident.evidence_ids,
        recovery_action=incident.recovery_action,
        execution_allowed=False,
    )

    return updated, transition


def plan_containment(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.CONTAINMENT_PLANNED,
        reason=reason,
    )


def request_containment_review(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.CONTAINMENT_REVIEW,
        reason=reason,
    )


def plan_recovery(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.RECOVERY_PLANNED,
        reason=reason,
    )


def request_recovery_review(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.RECOVERY_REVIEW,
        reason=reason,
    )


def resolve_incident(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.RESOLVED,
        reason=reason,
    )


def lock_incident(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.LOCKED,
        reason=reason,
    )


def fail_incident(
    incident: Incident,
    *,
    reason: str,
) -> tuple[Incident, Transition]:
    return transition_incident(
        incident,
        IncidentState.FAILED,
        reason=reason,
    )


def transition_to_dict(
    transition: Transition,
) -> dict[str, Any]:
    return {
        "incident_id": transition.incident_id,
        "previous_state": transition.previous_state.value,
        "new_state": transition.new_state.value,
        "reason": transition.reason,
        "execution_allowed": transition.execution_allowed,
        "human_review_required": transition.human_review_required,
        "dry_run": transition.dry_run,
        "real_execution_blocked": transition.real_execution_blocked,
        "response_locked": transition.response_locked,
    }


def incident_to_dict(
    incident: Incident,
) -> dict[str, Any]:
    return {
        "incident_id": incident.incident_id,
        "state": incident.state.value,
        "risk_level": incident.risk_level,
        "target": incident.target,
        "reason": incident.reason,
        "evidence_ids": list(incident.evidence_ids),
        "recovery_action": incident.recovery_action.value,
        "execution_allowed": incident.execution_allowed,
    }


def fail_closed(incident: Incident) -> bool:
    return (
        incident.execution_allowed is False
        and READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )
