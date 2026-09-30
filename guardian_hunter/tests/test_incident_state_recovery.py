from pathlib import Path

import pytest

from guardian_hunter.incident.state import (
    IncidentState,
    can_transition,
    create_incident,
    fail_closed,
    lock_incident,
    plan_containment,
    plan_recovery,
    request_containment_review,
    request_recovery_review,
    resolve_incident,
    safety_invariants_hold,
    transition_incident,
)


def test_safety_invariants():
    assert safety_invariants_hold()


def test_new_incident_is_fail_closed():
    incident = create_incident(
        incident_id="inc-001",
        risk_level="HIGH",
        target="host-a",
        reason="controlled test",
    )

    assert incident.state == IncidentState.NEW
    assert incident.execution_allowed is False
    assert fail_closed(incident)


def test_normal_containment_to_recovery_path():
    incident = create_incident(
        incident_id="inc-002",
        risk_level="HIGH",
        target="host-b",
        reason="controlled test",
    )

    incident, transition = transition_incident(
        incident,
        IncidentState.TRIAGED,
        reason="triage completed",
    )

    assert transition.execution_allowed is False

    incident, _ = transition_incident(
        incident,
        IncidentState.AUTHORIZED,
        reason="authorization recorded",
    )

    incident, _ = plan_containment(
        incident,
        reason="containment plan prepared",
    )

    incident, _ = request_containment_review(
        incident,
        reason="human review required",
    )

    incident, _ = plan_recovery(
        incident,
        reason="recovery plan prepared",
    )

    incident, _ = request_recovery_review(
        incident,
        reason="recovery review required",
    )

    incident, _ = resolve_incident(
        incident,
        reason="resolution recorded",
    )

    assert incident.state == IncidentState.RESOLVED
    assert fail_closed(incident)


def test_invalid_transition_is_rejected():
    incident = create_incident(
        incident_id="inc-003",
        risk_level="MEDIUM",
        target="host-c",
        reason="controlled test",
    )

    assert not can_transition(
        IncidentState.NEW,
        IncidentState.RESOLVED,
    )

    with pytest.raises(ValueError):
        transition_incident(
            incident,
            IncidentState.RESOLVED,
            reason="invalid transition",
        )


def test_locked_incident_cannot_continue():
    incident = create_incident(
        incident_id="inc-004",
        risk_level="CRITICAL",
        target="host-d",
        reason="controlled test",
    )

    incident, _ = lock_incident(
        incident,
        reason="fail-closed lock",
    )

    assert incident.state == IncidentState.LOCKED

    with pytest.raises(ValueError):
        transition_incident(
            incident,
            IncidentState.TRIAGED,
            reason="must remain locked",
        )

    assert fail_closed(incident)


def test_failed_incident_can_only_lock():
    incident = create_incident(
        incident_id="inc-005",
        risk_level="HIGH",
        target="host-e",
        reason="controlled test",
    )

    incident, _ = transition_incident(
        incident,
        IncidentState.FAILED,
        reason="controlled failure",
    )

    assert incident.state == IncidentState.FAILED

    with pytest.raises(ValueError):
        transition_incident(
            incident,
            IncidentState.RECOVERY_PLANNED,
            reason="invalid recovery",
        )

    incident, _ = lock_incident(
        incident,
        reason="failure lock",
    )

    assert incident.state == IncidentState.LOCKED
    assert fail_closed(incident)
