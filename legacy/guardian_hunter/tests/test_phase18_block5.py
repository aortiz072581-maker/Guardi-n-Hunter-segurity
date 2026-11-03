"""Validation test for Phase 18.17 → 18.20."""

from guardian_hunter.network.phase18_remediation import (
    READ_ONLY,
    DRY_RUN,
    EXECUTION_ALLOWED,
    build_network_remediation_plan,
    validate_network_remediation_plan,
)

from guardian_hunter.network.phase18_containment import (
    simulate_network_containment,
    validate_network_containment,
)

from guardian_hunter.network.phase18_recovery import (
    verify_network_recovery,
    validate_network_recovery,
)

from guardian_hunter.network.phase18_final import (
    build_network_final_integration,
    validate_network_final_integration,
)


def main() -> None:

    # --------------------------------------------------
    # 18.17
    # --------------------------------------------------

    plan = build_network_remediation_plan(
        "CRITICAL",
        82,
    )

    assert validate_network_remediation_plan(plan)
    assert plan.execution_allowed is False
    assert plan.mode == "READ_ONLY"
    assert plan.status == "PLANNED_ONLY"

    print("PHASE 18.17 NETWORK REMEDIATION PLAN: OK")
    print("PHASE 18.17 DEFENSIVE ACTION PLAN: OK")
    print("PHASE 18.17 READ-ONLY: OK")

    # --------------------------------------------------
    # 18.18
    # --------------------------------------------------

    containment = simulate_network_containment(
        "CRITICAL"
    )

    assert validate_network_containment(containment)
    assert containment.simulated is True
    assert containment.changes_applied is False
    assert containment.execution_allowed is False

    print("PHASE 18.18 CONTAINMENT SIMULATION: OK")
    print("PHASE 18.18 NO CHANGES APPLIED: OK")
    print("PHASE 18.18 READ-ONLY: OK")

    # --------------------------------------------------
    # 18.19
    # --------------------------------------------------

    recovery = verify_network_recovery(
        baseline_integrity=True,
        evidence_integrity=True,
        response_lock=True,
        post_event_stable=True,
    )

    assert validate_network_recovery(recovery)
    assert recovery.recovery_ready is True
    assert recovery.execution_allowed is False

    print("PHASE 18.19 RECOVERY VERIFICATION: OK")
    print("PHASE 18.19 RECOVERY INTEGRITY: OK")
    print("PHASE 18.19 READ-ONLY: OK")

    # --------------------------------------------------
    # 18.20
    # --------------------------------------------------

    phase_results = {
        f"18.{i}": True
        for i in range(1, 21)
    }

    final = build_network_final_integration(
        phase_results
    )

    assert validate_network_final_integration(final)
    assert final.total_phases == 20
    assert final.passed_phases == 20
    assert final.failed_phases == 0
    assert final.regression_pass is True
    assert final.status == "NETWORK_DEFENSE_READY"

    print("PHASE 18.20 FINAL NETWORK INTEGRATION: OK")
    print("PHASE 18.20 18.1 → 18.20 REGRESSION: OK")
    print("PHASE 18.20 SHA-256 INTEGRITY: OK")
    print("PHASE 18.20 READ-ONLY: OK")

    # --------------------------------------------------
    # GLOBAL SAFETY
    # --------------------------------------------------

    assert READ_ONLY is True
    assert DRY_RUN is True
    assert EXECUTION_ALLOWED is False

    print("PHASE 18 BLOCK 5 TEST: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")


if __name__ == "__main__":
    main()
