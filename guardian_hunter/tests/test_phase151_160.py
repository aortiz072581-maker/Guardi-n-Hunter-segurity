"""Phases 151→160 buyer-ready release validation."""

from guardian_hunter.release.release_manifest import (
    build_release_manifest,
)

from guardian_hunter.due_diligence.dependency_inventory import (
    DependencyRecord,
    validate_dependency,
)

from guardian_hunter.release.test_evidence import (
    build_test_evidence,
)

from guardian_hunter.release.release_readiness import (
    audit_release,
)

from guardian_hunter.product.buyer_readiness import (
    final_buyer_audit,
)


def test_phase151_release_manifest():

    result = build_release_manifest()

    assert result.product == "Guardian Hunter"
    assert result.release_stage == "BUYER_EVALUATION"

    assert result.read_only is True
    assert result.dry_run is True
    assert result.real_execution_blocked is True
    assert result.human_review_required is True
    assert result.response_locked is True
    assert result.execution_allowed is False


def test_phase152_dependency_validation():

    dependency = DependencyRecord(
        name="example-package",
        version="1.0.0",
        ecosystem="python",
        license_status="DOCUMENTED",
    )

    assert validate_dependency(dependency) is True


def test_phase153_test_evidence():

    evidence = build_test_evidence(
        suite_name="guardian-hunter-release",
        tests_executed=10,
        tests_passed=10,
        tests_failed=0,
    )

    assert evidence.tests_executed == 10
    assert evidence.tests_passed == 10
    assert evidence.tests_failed == 0
    assert evidence.execution_allowed is False
    assert evidence.response_locked is True


def test_phase159_release_readiness():

    result = audit_release()

    assert result.ready is True
    assert result.completed == result.required
    assert result.execution_allowed is False
    assert result.human_review_required is True
    assert result.response_locked is True


def test_phase160_buyer_readiness():

    result = final_buyer_audit()

    assert result.product_ready is True
    assert result.release_ready is True
    assert result.evidence_ready is True

    # IP still requires formal human/legal review.
    assert result.ip_review_required is True

    assert result.human_review_required is True
    assert result.execution_allowed is False
    assert result.response_locked is True


def test_global_safety_contract():

    from guardian_hunter.runtime.node_runtime import (
        READ_ONLY,
        DRY_RUN,
        REAL_EXECUTION_BLOCKED,
        HUMAN_REVIEW_REQUIRED,
        RESPONSE_LOCKED,
    )

    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True
