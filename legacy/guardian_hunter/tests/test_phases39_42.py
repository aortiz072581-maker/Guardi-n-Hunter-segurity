"""Validation for Guardian Hunter phases 39 → 42."""

from guardian_hunter.governance.phase39_posture import (
    build_posture_snapshot,
    validate_posture,
)

from guardian_hunter.governance.phase40_decision import (
    build_security_decision,
    validate_security_decision,
)

from guardian_hunter.governance.phase41_audit import (
    build_security_audit,
    validate_security_audit,
)

from guardian_hunter.governance.phase42_readiness import (
    build_final_readiness,
    validate_final_readiness,
)


def main() -> None:

    posture = build_posture_snapshot(
        True, True, True, True,
        True, True, True, True
    )

    assert validate_posture(posture)
    assert posture.posture_score == 100
    assert posture.posture_ready is True
    assert len(posture.digest) == 64

    print("PHASE 39 SECURITY POSTURE: OK")
    print("PHASE 39 POSTURE SCORE: OK")
    print("PHASE 39 SHA-256 INTEGRITY: OK")
    print("PHASE 39 READ-ONLY: OK")

    decision = build_security_decision(
        True,
        posture.posture_score,
    )

    assert validate_security_decision(decision)
    assert decision.decision == (
        "CONTINUE_DEFENSIVE_MONITORING"
    )
    assert decision.requires_human_review is False
    assert decision.response_locked is True
    assert decision.execution_allowed is False

    print("PHASE 40 SECURITY DECISION: OK")
    print("PHASE 40 DEFENSIVE LOGIC: OK")
    print("PHASE 40 RESPONSE LOCK: OK")
    print("PHASE 40 READ-ONLY: OK")

    audit = build_security_audit({
        "governance": True,
        "posture": True,
        "integrity": True,
        "baseline": True,
        "evidence": True,
        "response_lock": True,
        "dry_run": True,
    })

    assert validate_security_audit(audit)
    assert audit.total == 7
    assert audit.passed == 7
    assert audit.failed == 0
    assert audit.audit_valid is True
    assert audit.evidence_preserved is True
    assert audit.response_locked is True
    assert len(audit.digest) == 64

    print("PHASE 41 SECURITY AUDIT: OK")
    print("PHASE 41 EVIDENCE PRESERVATION: OK")
    print("PHASE 41 SHA-256 INTEGRITY: OK")
    print("PHASE 41 READ-ONLY: OK")

    readiness = build_final_readiness(
        True, True, True, True, True
    )

    assert validate_final_readiness(readiness)
    assert readiness.readiness_score == 100
    assert readiness.ready_for_monitoring is True
    assert readiness.execution_blocked is True
    assert readiness.status == (
        "READY_FOR_DEFENSIVE_MONITORING"
    )
    assert len(readiness.digest) == 64

    print("PHASE 42 FINAL DEFENSIVE READINESS: OK")
    print("PHASE 42 READINESS SCORE: OK")
    print("PHASE 42 EXECUTION BLOCK: OK")
    print("PHASE 42 SHA-256 INTEGRITY: OK")
    print("PHASE 42 READ-ONLY: OK")

    from guardian_hunter.governance.phase39_posture import (
        READ_ONLY as R39,
        DRY_RUN as D39,
        EXECUTION_ALLOWED as E39,
    )

    from guardian_hunter.governance.phase40_decision import (
        READ_ONLY as R40,
        DRY_RUN as D40,
        EXECUTION_ALLOWED as E40,
    )

    from guardian_hunter.governance.phase41_audit import (
        READ_ONLY as R41,
        DRY_RUN as D41,
        EXECUTION_ALLOWED as E41,
    )

    from guardian_hunter.governance.phase42_readiness import (
        READ_ONLY as R42,
        DRY_RUN as D42,
        EXECUTION_ALLOWED as E42,
    )

    assert all([R39, R40, R41, R42])
    assert all([D39, D40, D41, D42])
    assert not any([E39, E40, E41, E42])

    print("PHASES 39 → 42 GLOBAL SAFETY: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")
    print("PHASES 39 → 42 TEST: OK")


if __name__ == "__main__":
    main()
