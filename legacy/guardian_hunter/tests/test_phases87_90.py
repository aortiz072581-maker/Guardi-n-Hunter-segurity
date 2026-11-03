from guardian_hunter.governance.phase87_response_review import (
    build_response_review,
    validate_response_review,
)

from guardian_hunter.verification.phase88_response_integrity import (
    build_response_integrity,
    validate_response_integrity,
)

from guardian_hunter.governance.phase89_response_assurance import (
    build_response_assurance,
    validate_response_assurance,
)

from guardian_hunter.governance.phase90_response_continuity import (
    build_response_continuity,
    validate_response_continuity,
)


def test_phases87_90():

    review = build_response_review(
        score=100,
        response_locked=True,
        human_review_required=True,
    )

    integrity = build_response_integrity(
        score=review.score,
        response_locked=review.response_locked,
        human_review_required=review.human_review_required,
    )

    assurance = build_response_assurance(
        score=integrity.score,
        integrity_valid=integrity.integrity_valid,
        response_locked=integrity.response_locked,
        human_review_required=integrity.human_review_required,
    )

    continuity = build_response_continuity(
        score=assurance.score,
        assurance_valid=assurance.assurance_valid,
        response_locked=assurance.response_locked,
        human_review_required=assurance.human_review_required,
    )

    assert validate_response_review(review)
    assert validate_response_integrity(integrity)
    assert validate_response_assurance(assurance)
    assert validate_response_continuity(continuity)

    assert review.score == 100
    assert integrity.score == 100
    assert assurance.score == 100
    assert continuity.score == 100

    assert continuity.state == "DEFENSIVE_RESPONSE_CONTINUOUS"
    assert continuity.continuity_valid is True
    assert continuity.response_locked is True
    assert continuity.human_review_required is True

    assert continuity.read_only is True
    assert continuity.dry_run is True
    assert continuity.execution_allowed is False

    assert len(integrity.digest) == 64
    assert len(continuity.digest) == 64

    print("87 DEFENSIVE RESPONSE REVIEW: OK")
    print("88 DEFENSIVE RESPONSE INTEGRITY: OK")
    print("89 DEFENSIVE RESPONSE ASSURANCE: OK")
    print("90 DEFENSIVE RESPONSE CONTINUITY: OK")
    print("87 → 90 REGRESSION: OK")
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
    test_phases87_90()
