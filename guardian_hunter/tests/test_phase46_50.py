"""Tests for phases 46-50."""

from guardian_hunter.audit.phase46 import (
    AuditTrail,
    build_audit_report,
    create_audit_event,
    validate_audit_trail,
)
from guardian_hunter.baseline.phase47 import (
    build_baseline_report,
    compare_baseline,
    create_baseline,
    verify_baseline,
)
from guardian_hunter.compliance.phase48 import (
    assess_compliance,
    build_compliance_report,
    validate_compliance,
)
from guardian_hunter.finalization.phase49 import (
    build_posture_report,
    build_security_posture,
    validate_security_posture,
)
from guardian_hunter.finalization.phase50 import (
    build_final_report,
    finalize_system,
    validate_final_integrity,
)


def main():
    # ==================================================
    # PHASE 46
    # ==================================================

    trail = AuditTrail()

    trail.add(
        create_audit_event(
            "AUD-001",
            "CASE_CREATED",
            "case_manager",
            "Security case created",
            "INFO",
        )
    )

    trail.add(
        create_audit_event(
            "AUD-002",
            "RISK_ANALYZED",
            "risk_analytics",
            "Risk analytics completed",
            "HIGH",
        )
    )

    assert trail.count() == 2
    assert validate_audit_trail(trail) is True

    audit_report = build_audit_report(trail)

    assert audit_report["phase"] == 46
    assert audit_report["mode"] == "READ_ONLY"
    assert audit_report["execution_allowed"] is False

    print("PHASE 46 AUDIT TRAIL: OK")
    print("PHASE 46 FORENSIC TRACE: OK")
    print("PHASE 46 READ-ONLY: OK")

    # ==================================================
    # PHASE 47
    # ==================================================

    baseline = create_baseline(
        "BASE-47",
        {
            "gateway": "192.168.1.1",
            "dns": "192.168.1.1",
            "mode": "monitoring",
        },
    )

    assert verify_baseline(baseline) is True

    comparison = compare_baseline(
        baseline,
        {
            "gateway": "192.168.1.1",
            "dns": "192.168.1.1",
            "mode": "monitoring",
        },
    )

    assert comparison["integrity"] is True
    assert comparison["changed_count"] == 0
    assert comparison["execution_allowed"] is False

    baseline_report = build_baseline_report(baseline)

    assert baseline_report["phase"] == 47
    assert baseline_report["execution_allowed"] is False

    print("PHASE 47 BASELINE INTEGRITY: OK")
    print("PHASE 47 BASELINE COMPARISON: OK")
    print("PHASE 47 READ-ONLY: OK")

    # ==================================================
    # PHASE 48
    # ==================================================

    compliance = assess_compliance(
        {
            "audit_logging": True,
            "baseline_validation": True,
            "evidence_integrity": True,
            "risk_analytics": True,
            "readiness_assessment": True,
            "response_lock": True,
        }
    )

    assert compliance.compliance == "COMPLIANT"
    assert compliance.controls_checked == 6
    assert compliance.controls_passed == 6
    assert compliance.controls_failed == 0
    assert compliance.execution_allowed is False
    assert validate_compliance(compliance) is True

    compliance_report = build_compliance_report(compliance)

    assert compliance_report["phase"] == 48
    assert compliance_report["execution_allowed"] is False

    print("PHASE 48 DEFENSIVE COMPLIANCE: OK")
    print("PHASE 48 CONTROL VALIDATION: OK")
    print("PHASE 48 READ-ONLY: OK")

    # ==================================================
    # PHASE 49
    # ==================================================

    posture = build_security_posture(
        case_state="INVESTIGATING",
        risk_score=72.5,
        readiness="READY",
        compliance="COMPLIANT",
        audit_events=2,
        baseline_integrity=True,
    )

    assert validate_security_posture(posture) is True
    assert posture.execution_allowed is False

    posture_report = build_posture_report(posture)

    assert posture_report["phase"] == 49
    assert posture_report["execution_allowed"] is False
    assert posture_report["baseline_integrity"] is True

    print("PHASE 49 SECURITY POSTURE: OK")
    print("PHASE 49 INTEGRITY SNAPSHOT: OK")
    print("PHASE 49 READ-ONLY: OK")

    # ==================================================
    # PHASE 50
    # ==================================================

    final = finalize_system(
        audit_valid=validate_audit_trail(trail),
        baseline_valid=verify_baseline(baseline),
        compliance_valid=validate_compliance(compliance),
        posture_valid=validate_security_posture(posture),
        readiness_valid=True,
    )

    assert final.phases_validated == 5
    assert final.final_status == "READY_FOR_DEFENSIVE_MONITORING"
    assert final.execution_allowed is False
    assert validate_final_integrity(final) is True

    final_report = build_final_report(final)

    assert final_report["phase"] == 50
    assert final_report["dry_run"] is True
    assert final_report["execution_allowed"] is False

    print("PHASE 50 FINAL INTEGRITY: OK")
    print("PHASE 50 RELEASE GATE: OK")
    print("PHASE 50 READ-ONLY: OK")
    print("PHASE 50 DRY-RUN: LOCKED")
    print("REAL EXECUTION: BLOCKED")
    print("PHASE 46-50 TEST: OK")


if __name__ == "__main__":
    main()
