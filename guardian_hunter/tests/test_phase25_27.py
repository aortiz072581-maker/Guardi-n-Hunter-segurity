"""Integration tests for phases 25-27."""

from guardian_hunter.response.phase25 import (
    approve_workflow,
    create_response_workflow,
    rollback_workflow,
    verify_workflow,
)

from guardian_hunter.hardening.phase26 import (
    baseline_integrity,
    classify_changes,
    compare_baseline,
    create_baseline,
)

from guardian_hunter.health.monitor import (
    health_check,
    summarize_health,
)


def main() -> None:
    # ----------------------------------------------
    # PHASE 25
    # ----------------------------------------------

    decision = {
        "requires_approval": True,
        "execution_allowed": False,
        "mode": "DRY_RUN",
    }

    workflow = create_response_workflow(
        "INC-25-TEST",
        decision,
    )

    assert workflow["state"] == "PLANNED"
    assert workflow["mode"] == "DRY_RUN"
    assert workflow["execution_allowed"] is False
    assert workflow["rollback_available"] is True

    approved = approve_workflow(
        workflow,
        approved=True,
    )

    assert approved["state"] == "APPROVED"
    assert approved["execution_allowed"] is False

    verified = verify_workflow(approved)

    assert verified["verified"] is True
    assert verified["verification"]["execution_observed"] is False

    rolled_back = rollback_workflow(verified)

    assert rolled_back["state"] == "ROLLED_BACK"
    assert rolled_back["execution_allowed"] is False

    print("PHASE 25 ORCHESTRATOR 2.0: OK")
    print("PHASE 25 EXECUTION LOCK: OK")
    print("PHASE 25 ROLLBACK: OK")

    # ----------------------------------------------
    # PHASE 26
    # ----------------------------------------------

    snapshot = {
        "platform": "test",
        "network": "safe",
        "version": 1,
    }

    baseline = create_baseline(snapshot)

    assert baseline_integrity(baseline) is True

    same = compare_baseline(
        baseline,
        dict(snapshot),
    )

    assert same["unchanged"] is True
    assert same["change_count"] == 0

    changed = dict(snapshot)
    changed["version"] = 2
    changed["new_setting"] = "expected"

    comparison = compare_baseline(
        baseline,
        changed,
    )

    assert comparison["unchanged"] is False
    assert comparison["change_count"] == 2

    classification = classify_changes(
        comparison,
        expected_changes={"version", "new_setting"},
    )

    assert classification["status"] == "EXPECTED_CHANGE"
    assert not classification["unexpected_changes"]

    unexpected = classify_changes(
        comparison,
        expected_changes={"version"},
    )

    assert unexpected["status"] == "UNEXPECTED_CHANGE"
    assert "new_setting" in unexpected["unexpected_changes"]

    print("PHASE 26 INTELLIGENT BASELINE: OK")
    print("PHASE 26 CHANGE CLASSIFICATION: OK")
    print("PHASE 26 INTEGRITY: OK")

    # ----------------------------------------------
    # PHASE 27
    # ----------------------------------------------

    summary = health_check(
        modules=[
            "guardian_hunter",
            "guardian_hunter.decision.engine",
            "guardian_hunter.correlation.advanced",
            "guardian_hunter.evidence.incident",
            "guardian_hunter.response.phase25",
            "guardian_hunter.hardening.phase26",
            "guardian_hunter.health.monitor",
        ]
    )

    assert summary["status"] == "HEALTHY"
    assert summary["error_modules"] == 0
    assert summary["healthy_modules"] == summary["total_modules"]

    manual = summarize_health(
        [
            {
                "module": "test",
                "status": "OK",
                "error": None,
            }
        ]
    )

    assert manual["status"] == "HEALTHY"

    print("PHASE 27 HEALTH MONITOR: OK")
    print("PHASE 27 MODULE HEALTH: OK")
    print("PHASE 25-27 TEST: OK")


if __name__ == "__main__":
    main()
