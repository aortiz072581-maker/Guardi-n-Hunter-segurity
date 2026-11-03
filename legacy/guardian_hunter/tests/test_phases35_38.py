"""Validation for Guardian Hunter phases 35 → 38."""

from guardian_hunter.governance.phase35_controls import (
    build_control_matrix,
    validate_control_matrix,
)

from guardian_hunter.verification.phase36_integrity import (
    verify_security_integrity,
    validate_security_integrity,
)

from guardian_hunter.governance.phase37_continuity import (
    build_security_continuity,
    validate_security_continuity,
)

from guardian_hunter.governance.phase38_operations import (
    build_operations_gate,
    validate_operations_gate,
)


def main() -> None:

    # ==================================================
    # PHASE 35
    # ==================================================

    matrix = build_control_matrix()

    assert validate_control_matrix(matrix)
    assert matrix.total_controls == 8
    assert matrix.passed_controls == 8
    assert matrix.failed_controls == 0
    assert matrix.coverage_percent == 100
    assert matrix.complete is True
    assert matrix.response_locked is True

    print("PHASE 35 SECURITY CONTROL MATRIX: OK")
    print("PHASE 35 CONTROL COVERAGE: OK")
    print("PHASE 35 RESPONSE LOCK: OK")
    print("PHASE 35 READ-ONLY: OK")

    # ==================================================
    # PHASE 36
    # ==================================================

    integrity = verify_security_integrity({
        "core": True,
        "baseline": True,
        "evidence": True,
        "audit": True,
        "response": True,
        "governance": True,
    })

    assert validate_security_integrity(integrity)
    assert integrity.total_components == 6
    assert integrity.valid_components == 6
    assert integrity.invalid_components == 0
    assert integrity.integrity_score == 100
    assert integrity.integrity_valid is True
    assert len(integrity.digest) == 64

    print("PHASE 36 SECURITY INTEGRITY: OK")
    print("PHASE 36 INTEGRITY SCORE: OK")
    print("PHASE 36 SHA-256: OK")
    print("PHASE 36 READ-ONLY: OK")

    # ==================================================
    # PHASE 37
    # ==================================================

    continuity = build_security_continuity({
        "monitoring": True,
        "audit": True,
        "evidence": True,
        "baseline": True,
        "health": True,
        "response_lock": True,
    })

    assert validate_security_continuity(continuity)
    assert continuity.total_safeguards == 6
    assert continuity.active_safeguards == 6
    assert continuity.inactive_safeguards == 0
    assert continuity.continuity_score == 100
    assert continuity.continuity_ready is True
    assert continuity.response_locked is True

    print("PHASE 37 SECURITY CONTINUITY: OK")
    print("PHASE 37 SAFEGUARDS: OK")
    print("PHASE 37 CONTINUITY GATE: OK")
    print("PHASE 37 READ-ONLY: OK")

    # ==================================================
    # PHASE 38
    # ==================================================

    gate = build_operations_gate(
        control_matrix_ok=True,
        integrity_ok=True,
        continuity_ok=True,
        audit_ok=True,
        evidence_ok=True,
        baseline_ok=True,
        response_locked=True,
    )

    assert validate_operations_gate(gate)
    assert gate.safety_score == 100
    assert gate.operations_ready is True
    assert gate.execution_blocked is True
    assert gate.status == "DEFENSIVE_OPERATIONS_READY"
    assert len(gate.digest) == 64

    print("PHASE 38 DEFENSIVE OPERATIONS GATE: OK")
    print("PHASE 38 SAFETY SCORE: OK")
    print("PHASE 38 EXECUTION BLOCK: OK")
    print("PHASE 38 SHA-256 INTEGRITY: OK")
    print("PHASE 38 READ-ONLY: OK")

    # ==================================================
    # GLOBAL SAFETY
    # ==================================================

    from guardian_hunter.governance.phase35_controls import (
        READ_ONLY as R35,
        DRY_RUN as D35,
        EXECUTION_ALLOWED as E35,
    )

    from guardian_hunter.verification.phase36_integrity import (
        READ_ONLY as R36,
        DRY_RUN as D36,
        EXECUTION_ALLOWED as E36,
    )

    from guardian_hunter.governance.phase37_continuity import (
        READ_ONLY as R37,
        DRY_RUN as D37,
        EXECUTION_ALLOWED as E37,
    )

    from guardian_hunter.governance.phase38_operations import (
        READ_ONLY as R38,
        DRY_RUN as D38,
        EXECUTION_ALLOWED as E38,
    )

    assert all([R35, R36, R37, R38])
    assert all([D35, D36, D37, D38])
    assert not any([E35, E36, E37, E38])

    print("PHASES 35 → 38 GLOBAL SAFETY: OK")
    print("READ_ONLY: TRUE")
    print("DRY_RUN: TRUE")
    print("REAL EXECUTION: BLOCKED")
    print("PHASES 35 → 38 TEST: OK")


if __name__ == "__main__":
    main()
