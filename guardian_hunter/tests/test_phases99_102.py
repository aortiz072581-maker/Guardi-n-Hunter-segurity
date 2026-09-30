from guardian_hunter.governance.phase99_response_control import (
    build_response_control,
    validate_response_control,
)

from guardian_hunter.verification.phase100_response_evidence import (
    build_response_evidence,
    validate_response_evidence,
)

from guardian_hunter.governance.phase101_response_audit import (
    build_response_audit,
    validate_response_audit,
)

from guardian_hunter.governance.phase102_response_final import (
    build_response_final,
    validate_response_final,
)


def test_phases99_102():

    control = build_response_control(
        score=100,
        response_locked=True,
        human_review_required=True,
    )

    evidence = build_response_evidence(
        score=control.score,
        control_valid=control.control_valid,
        response_locked=control.response_locked,
        human_review_required=control.human_review_required,
    )

    audit = build_response_audit(
        score=evidence.score,
        evidence_valid=evidence.evidence_valid,
        response_locked=evidence.response_locked,
        human_review_required=evidence.human_review_required,
    )

    final = build_response_final(
        score=audit.score,
        audit_valid=audit.audit_valid,
        response_locked=audit.response_locked,
        human_review_required=audit.human_review_required,
    )

    assert validate_response_control(control)
    assert validate_response_evidence(evidence)
    assert validate_response_audit(audit)
    assert validate_response_final(final)

    assert control.score == 100
    assert evidence.score == 100
    assert audit.score == 100
    assert final.score == 100

    assert final.state == "DEFENSIVE_RESPONSE_FINAL_CONTINUOUS"
    assert final.final_valid is True
    assert final.response_locked is True
    assert final.human_review_required is True
    assert final.read_only is True
    assert final.dry_run is True
    assert final.execution_allowed is False

    assert len(evidence.digest) == 64
    assert len(final.digest) == 64

    print("99 DEFENSIVE RESPONSE CONTROL: OK")
    print("100 DEFENSIVE RESPONSE EVIDENCE: OK")
    print("101 DEFENSIVE RESPONSE AUDIT: OK")
    print("102 DEFENSIVE RESPONSE FINAL: OK")
    print("99 → 102 REGRESSION: OK")
    print("RESPONSE SCORE:", final.score)
    print("RESPONSE STATE:", final.state)
    print("RESPONSE LOCKED:", final.response_locked)
    print("HUMAN REVIEW REQUIRED:", final.human_review_required)
    print("READ_ONLY:", final.read_only)
    print("DRY_RUN:", final.dry_run)
    print(
        "REAL EXECUTION:",
        "BLOCKED" if not final.execution_allowed else "ENABLED",
    )


if __name__ == "__main__":
    test_phases99_102()
