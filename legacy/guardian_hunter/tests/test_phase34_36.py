"""Tests for phases 34-36."""

from guardian_hunter.incident.lifecycle import (
    create_incident,
    validate_lifecycle,
)
from guardian_hunter.recovery.planner import (
    create_recovery_plan,
    resilience_check,
    validate_recovery,
)
from guardian_hunter.assurance.continuous import (
    evaluate_assurance,
    assurance_gate,
    build_assurance_report,
)


def main() -> None:
    # ----------------------------------------------
    # PHASE 34
    # ----------------------------------------------
    incident = create_incident("INC-34-001")

    assert incident.state == "DETECTED"
    assert incident.mode == "DRY_RUN"
    assert incident.execution_allowed is False

    incident.transition("INVESTIGATING", "initial analysis")
    incident.transition("CONTAINMENT_REVIEW", "defensive review")
    incident.transition("RECOVERY_REVIEW", "recovery planning")
    incident.transition("CLOSED", "simulation completed")

    assert incident.state == "CLOSED"
    assert validate_lifecycle(incident)

    print("PHASE 34 INCIDENT LIFECYCLE: OK")
    print("PHASE 34 EXECUTION LOCK: OK")

    # ----------------------------------------------
    # PHASE 35
    # ----------------------------------------------
    plan = create_recovery_plan(incident.incident_id)

    plan.add_step(
        "Validate evidence",
        "integrity",
    )
    plan.add_step(
        "Validate baseline",
        "integrity",
    )
    plan.add_step(
        "Verify service health",
        "health",
    )

    result = plan.simulate()

    assert result["mode"] == "SIMULATION"
    assert result["executed"] is False
    assert result["execution_allowed"] is False
    assert validate_recovery(plan)

    resilience = resilience_check(
        evidence_integrity=True,
        baseline_integrity=True,
        audit_integrity=True,
        health_ok=True,
    )

    assert resilience["status"] == "RESILIENT"
    assert resilience["execution_allowed"] is False

    print("PHASE 35 RECOVERY PLANNER: OK")
    print("PHASE 35 RESILIENCE CHECK: OK")
    print("PHASE 35 EXECUTION BLOCK: OK")

    # ----------------------------------------------
    # PHASE 36
    # ----------------------------------------------
    assurance = evaluate_assurance(
        health=True,
        policy=True,
        audit=True,
        evidence=True,
        baseline=True,
        response_locked=True,
    )

    assert assurance["status"] == "ASSURED"
    assert assurance["coverage_percent"] == 100.0
    assert assurance["execution_allowed"] is False
    assert assurance_gate(assurance)

    report = build_assurance_report(assurance)

    assert report["read_only"] is True
    assert report["execution_blocked"] is True

    print("PHASE 36 CONTINUOUS ASSURANCE: OK")
    print("PHASE 36 ASSURANCE GATE: OK")
    print("PHASE 36 READ-ONLY: OK")

    print("PHASE 34-36 TEST: OK")


if __name__ == "__main__":
    main()
