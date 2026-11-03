from guardian_hunter.governance.phase103_response_system import (
    build_response_system,
    validate_response_system,
)

from guardian_hunter.verification.phase104_response_system_integrity import (
    build_response_system_integrity,
    validate_response_system_integrity,
)

from guardian_hunter.governance.phase105_response_release import (
    build_response_system_release,
    validate_response_system_release,
)

from guardian_hunter.governance.phase106_response_continuity import (
    build_response_system_continuity,
    validate_response_system_continuity,
)


def test_phases103_106():

    system = build_response_system(
        score=100,
        response_locked=True,
        human_review_required=True,
    )

    integrity = build_response_system_integrity(
        score=system.score,
        system_valid=system.system_valid,
        response_locked=system.response_locked,
        human_review_required=system.human_review_required,
    )

    release = build_response_system_release(
        score=integrity.score,
        integrity_valid=integrity.integrity_valid,
        response_locked=integrity.response_locked,
        human_review_required=integrity.human_review_required,
    )

    continuity = build_response_system_continuity(
        score=release.score,
        release_valid=release.release_valid,
        response_locked=release.response_locked,
        human_review_required=release.human_review_required,
    )

    assert validate_response_system(system)
    assert validate_response_system_integrity(integrity)
    assert validate_response_system_release(release)
    assert validate_response_system_continuity(continuity)

    assert system.score == 100
    assert integrity.score == 100
    assert release.score == 100
    assert continuity.score == 100

    assert continuity.state == "DEFENSIVE_RESPONSE_SYSTEM_CONTINUOUS"
    assert continuity.continuity_valid is True
    assert continuity.response_locked is True
    assert continuity.human_review_required is True
    assert continuity.read_only is True
    assert continuity.dry_run is True
    assert continuity.execution_allowed is False

    assert len(integrity.digest) == 64
    assert len(continuity.digest) == 64

    print("103 DEFENSIVE RESPONSE SYSTEM: OK")
    print("104 DEFENSIVE RESPONSE SYSTEM INTEGRITY: OK")
    print("105 DEFENSIVE RESPONSE SYSTEM RELEASE: OK")
    print("106 DEFENSIVE RESPONSE SYSTEM CONTINUITY: OK")
    print("103 → 106 REGRESSION: OK")
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
    test_phases103_106()
