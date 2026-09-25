"""Phase 31-33 validation tests."""

from guardian_hunter.audit.trail import (
    create_event,
    append_event,
    verify_trail,
)

from guardian_hunter.policy.guard import (
    evaluate_policy,
    policy_safe,
)

from guardian_hunter.simulation.safe import (
    simulate_incident,
    verify_simulation,
)


def test_phase31():
    trail = []

    first = create_event(
        event_type="TEST",
        source="PHASE31",
        details={"step": 1},
    )

    append_event(trail, first)

    second = create_event(
        event_type="TEST",
        source="PHASE31",
        details={"step": 2},
        previous_hash=first["hash"],
    )

    append_event(trail, second)

    result = verify_trail(trail)

    assert result["valid"] is True
    assert result["events"] == 2
    assert result["last_hash"] == second["hash"]

    print("PHASE 31 AUDIT TRAIL: OK")
    print("PHASE 31 HASH CHAIN: OK")


def test_phase32():
    safe = evaluate_policy(
        action="CONTAINMENT_REVIEW",
        mode="DRY_RUN",
        approved=False,
        execution_requested=False,
    )

    blocked = evaluate_policy(
        action="DELETE",
        mode="DRY_RUN",
        approved=True,
        execution_requested=True,
    )

    assert safe["execution_allowed"] is False
    assert safe["dry_run"] is True
    assert policy_safe(safe) is True

    assert blocked["allowed"] is False
    assert blocked["execution_allowed"] is False
    assert "ACTION_BLOCKED_BY_POLICY" in blocked["reasons"]
    assert "REAL_EXECUTION_DISABLED" in blocked["reasons"]

    print("PHASE 32 POLICY GUARD: OK")
    print("PHASE 32 EXECUTION GATE: OK")


def test_phase33():
    result = simulate_incident(
        incident_id="SIM-033",
        risk_score=75,
        action="CONTAINMENT_REVIEW",
    )

    verification = verify_simulation(result)

    assert verification["valid"] is True
    assert result["executed"] is False
    assert result["execution_allowed"] is False
    assert result["audit_integrity"]["valid"] is True
    assert len(result["audit"]) == 3

    print("PHASE 33 SAFE SIMULATION: OK")
    print("PHASE 33 AUDIT INTEGRITY: OK")
    print("PHASE 33 EXECUTION BLOCK: OK")


if __name__ == "__main__":
    test_phase31()
    test_phase32()
    test_phase33()
    print("PHASE 31-33 TEST: OK")
