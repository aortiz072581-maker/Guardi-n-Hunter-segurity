from guardian_hunter.governance.phase95_response_governance import (
    build_response_governance,
    validate_response_governance,
)

from guardian_hunter.verification.phase96_response_chain import (
    build_response_integrity_chain,
    validate_response_integrity_chain,
)

from guardian_hunter.governance.phase97_response_release import (
    build_response_release_review,
    validate_response_release_review,
)

from guardian_hunter.governance.phase98_response_readiness import (
    build_response_readiness,
    validate_response_readiness,
)


def test_phases95_98():

    governance = build_response_governance(
        score=100,
        response_locked=True,
        human_review_required=True,
    )

    chain = build_response_integrity_chain(
        score=governance.score,
        governance_valid=governance.governance_valid,
        response_locked=governance.response_locked,
        human_review_required=governance.human_review_required,
    )

    release = build_response_release_review(
        score=chain.score,
        chain_valid=chain.chain_valid,
        response_locked=chain.response_locked,
        human_review_required=chain.human_review_required,
    )

    readiness = build_response_readiness(
        score=release.score,
        release_valid=release.release_valid,
        response_locked=release.response_locked,
        human_review_required=release.human_review_required,
    )

    assert validate_response_governance(governance)
    assert validate_response_integrity_chain(chain)
    assert validate_response_release_review(release)
    assert validate_response_readiness(readiness)

    assert governance.score == 100
    assert chain.score == 100
    assert release.score == 100
    assert readiness.score == 100

    assert readiness.state == (
        "DEFENSIVE_RESPONSE_READINESS_CONTINUOUS"
    )

    assert readiness.readiness_valid is True
    assert readiness.response_locked is True
    assert readiness.human_review_required is True
    assert readiness.read_only is True
    assert readiness.dry_run is True
    assert readiness.execution_allowed is False

    assert len(chain.digest) == 64
    assert len(readiness.digest) == 64

    print("95 DEFENSIVE RESPONSE GOVERNANCE: OK")
    print("96 DEFENSIVE RESPONSE INTEGRITY CHAIN: OK")
    print("97 DEFENSIVE RESPONSE RELEASE REVIEW: OK")
    print("98 DEFENSIVE RESPONSE READINESS: OK")
    print("95 → 98 REGRESSION: OK")
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
    test_phases95_98()
