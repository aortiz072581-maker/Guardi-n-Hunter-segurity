from guardian_hunter.governance.phase91_response_supervision import (
    build_response_supervision,
    validate_response_supervision,
)

from guardian_hunter.verification.phase92_response_reconciliation import (
    build_response_reconciliation,
    validate_response_reconciliation,
)

from guardian_hunter.governance.phase93_response_assurance import (
    build_response_assurance_gate,
    validate_response_assurance_gate,
)

from guardian_hunter.governance.phase94_response_operational_continuity import (
    build_response_operational_continuity,
    validate_response_operational_continuity,
)


def test_phases91_94():

    supervision = build_response_supervision(
        score=100,
        response_locked=True,
        human_review_required=True,
    )

    reconciliation = build_response_reconciliation(
        score=supervision.score,
        supervision_valid=supervision.supervision_valid,
        response_locked=supervision.response_locked,
        human_review_required=supervision.human_review_required,
    )

    assurance = build_response_assurance_gate(
        score=reconciliation.score,
        reconciliation_valid=reconciliation.reconciliation_valid,
        response_locked=reconciliation.response_locked,
        human_review_required=reconciliation.human_review_required,
    )

    continuity = build_response_operational_continuity(
        score=assurance.score,
        assurance_valid=assurance.assurance_valid,
        response_locked=assurance.response_locked,
        human_review_required=assurance.human_review_required,
    )

    assert validate_response_supervision(supervision)
    assert validate_response_reconciliation(reconciliation)
    assert validate_response_assurance_gate(assurance)
    assert validate_response_operational_continuity(continuity)

    assert supervision.score == 100
    assert reconciliation.score == 100
    assert assurance.score == 100
    assert continuity.score == 100

    assert continuity.state == (
        "DEFENSIVE_RESPONSE_OPERATIONALLY_CONTINUOUS"
    )

    assert continuity.continuity_valid is True
    assert continuity.response_locked is True
    assert continuity.human_review_required is True
    assert continuity.read_only is True
    assert continuity.dry_run is True
    assert continuity.execution_allowed is False

    assert len(reconciliation.digest) == 64
    assert len(continuity.digest) == 64

    print("91 DEFENSIVE RESPONSE SUPERVISION: OK")
    print("92 DEFENSIVE RESPONSE RECONCILIATION: OK")
    print("93 DEFENSIVE RESPONSE ASSURANCE: OK")
    print("94 DEFENSIVE RESPONSE OPERATIONAL CONTINUITY: OK")
    print("91 → 94 REGRESSION: OK")
    print("RESPONSE SCORE:", continuity.score)
    print("RESPONSE STATE:", continuity.state)
    print("RESPONSE LOCKED:", continuity.response_locked)
    print("HUMAN REVIEW REQUIRED:", continuity.human_review_required)
    print("READ_ONLY:", continuity.read_only)
    print("DRY_RUN:", continuity.dry_run)
    print(
        "REAL EXECUTION:",
        "BLOCKED" if not continuity.execution_allowed else "ENABLED",
    )


if __name__ == "__main__":
    test_phases91_94()
