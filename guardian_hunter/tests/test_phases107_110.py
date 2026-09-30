from guardian_hunter.governance.phase107_response_assurance import (
    build_response_assurance,
    validate_response_assurance,
)

from guardian_hunter.verification.phase108_response_traceability import (
    build_response_traceability,
    validate_response_traceability,
)

from guardian_hunter.governance.phase109_response_review import (
    build_response_final_review,
    validate_response_final_review,
)

from guardian_hunter.governance.phase110_response_readiness import (
    build_response_readiness,
    validate_response_readiness,
)


def test_phases107_110():

    assurance = build_response_assurance()

    traceability = build_response_traceability(
        score=assurance.score,
        assurance_valid=assurance.assurance_valid,
        response_locked=assurance.response_locked,
        human_review_required=assurance.human_review_required,
    )

    review = build_response_final_review(
        score=traceability.score,
        traceability_valid=traceability.traceability_valid,
        response_locked=traceability.response_locked,
        human_review_required=traceability.human_review_required,
    )

    readiness = build_response_readiness(
        score=review.score,
        review_valid=review.review_valid,
        response_locked=review.response_locked,
        human_review_required=review.human_review_required,
    )

    assert validate_response_assurance(assurance)
    assert validate_response_traceability(traceability)
    assert validate_response_final_review(review)
    assert validate_response_readiness(readiness)

    assert assurance.score == 100
    assert traceability.score == 100
    assert review.score == 100
    assert readiness.score == 100

    assert readiness.state == "DEFENSIVE_RESPONSE_OPERATIONAL_READY"
    assert readiness.readiness_valid is True
    assert readiness.response_locked is True
    assert readiness.human_review_required is True
    assert readiness.read_only is True
    assert readiness.dry_run is True
    assert readiness.execution_allowed is False

    assert len(traceability.digest) == 64
    assert len(readiness.digest) == 64

    print("107 DEFENSIVE RESPONSE ASSURANCE: OK")
    print("108 DEFENSIVE RESPONSE TRACEABILITY: OK")
    print("109 DEFENSIVE RESPONSE FINAL REVIEW: OK")
    print("110 DEFENSIVE RESPONSE OPERATIONAL READINESS: OK")
    print("107 → 110 REGRESSION: OK")
    print("RESPONSE SCORE:", readiness.score)
    print("RESPONSE STATE:", readiness.state)
    print("RESPONSE LOCKED:", readiness.response_locked)
    print("HUMAN REVIEW REQUIRED:", readiness.human_review_required)
    print("READ_ONLY:", readiness.read_only)
    print("DRY_RUN:", readiness.dry_run)
    print(
        "REAL EXECUTION:",
        "BLOCKED" if not readiness.execution_allowed else "ENABLED",
    )


if __name__ == "__main__":
    test_phases107_110()
