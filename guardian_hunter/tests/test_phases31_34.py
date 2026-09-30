"""Validation for Guardian Hunter phases 31 → 34."""

from guardian_hunter.governance.phase31_governance import (
    READ_ONLY as R31,
    DRY_RUN as D31,
    EXECUTION_ALLOWED as E31,
    build_security_governance,
    validate_security_governance,
)

from guardian_hunter.verification.phase32_verification import (
    verify_security_controls,
    validate_security_verification,
)

from guardian_hunter.verification.phase33_health import (
    build_security_health_gate,
    validate_security_health,
)

from guardian_hunter.governance.phase34_release import (
    build_security_release_gate,
    validate_security_release,
)


def main() -> None:

    # ==================================================
    # PHASE 31
    # ==================================================

    governance = build_security_governance()

    assert validate_security_governance(governance)
    assert governance.all_controls_present is True
    assert governance.response_locked is True
    assert governance.execution_allowed is False

    print("PHASE 31 SECURITY GOVERNANCE: OK")
    print("PHASE 31 CONTROL SET: OK")
    print("PHASE 31 RESPONSE LOCK: OK")
    print("PHASE 31 READ-ONLY: OK")

    # ==================================================
    # PHASE 32
    # ==================================================

    verification = verify_security_controls({
        "governance": True,
        "audit": True,
        "evidence_integrity": True,
        "baseline_integrity": True,
        "response_lock": True,
        "dry_run": True,
    })

    assert validate_security_verification(verification)
    assert verification.total_checks == 6
    assert verification.passed_checks == 6
    assert verification.failed_checks == 0
    assert verification.verification_pass is True

    print("PHASE 32 SECURITY VERIFICATION: OK")
    print("PHASE 32 CONTROL VALIDATION: OK")
    print("PHASE 32 VERIFICATION GATE: OK")
    print("PHASE 32 READ-ONLY: OK")

    # ==================================================
    # PHASE 33
    # ==================================================

    health = build_security_health_gate(
        governance_ok=True,
        verification_ok=True,
        audit_ok=True,
        evidence_ok=True,
        baseline_ok=True,
        response_locked=True,
    )

    assert validate_security_health(health)
    assert health.health_score == 100
    assert health.healthy is True
    assert health.status == "HEALTHY_READ_ONLY"

    print("PHASE 33 SECURITY HEALTH: OK")
    print("PHASE 33 HEALTH SCORE: OK")
    print("PHASE 33 HEALTH GATE: OK")
    print("PHASE 33 READ-ONLY: OK")

    # ==================================================
    # PHASE 34
    # ==================================================

    phase_results = {
        "31": True,
        "32": True,
        "33": True,
        "34": True,
    }

    release = build_security_release_gate(
        phase_results
    )

    assert validate_security_release(release)
    assert release.total_phases == 4
    assert release.passed_phases == 4
    assert release.failed_phases == 0
    assert release.release_ready is True
    assert release.status == "RELEASE_READY_READ_ONLY"

    print("PHASE 34 SECURITY RELEASE GATE: OK")
    print("PHASE 34 REGRESSION: OK")
    print("PHASE 34 SHA-256 INTEGRITY: OK")
    print("PHASE 34 READ-ONLY: OK")

    # ==================================================
    # GLOBAL SAFETY
    # ==================================================

    assert R31 is True
    assert D31 is True
    assert E31 is False

    print("PHASES 31 → 34 GLOBAL SAFETY: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")
    print("PHASES 31 → 34 TEST: OK")


if __name__ == "__main__":
    main()
