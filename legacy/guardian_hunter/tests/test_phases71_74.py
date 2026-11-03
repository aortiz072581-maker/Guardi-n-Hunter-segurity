from guardian_hunter.governance.phase71_baseline_continuity import (
    build_baseline_continuity,
    baseline_continuity_to_dict,
    validate_baseline_continuity,
)
from guardian_hunter.verification.phase72_integrity_reconciliation import (
    build_integrity_reconciliation,
    integrity_to_dict,
    validate_integrity_reconciliation,
)
from guardian_hunter.governance.phase73_final_review import (
    build_final_review,
    final_review_to_dict,
    validate_final_review,
)
from guardian_hunter.governance.phase74_monitoring_readiness import (
    build_monitoring_readiness,
    monitoring_readiness_to_dict,
    validate_monitoring_readiness,
)


def test_phase71():
    item = build_baseline_continuity()
    assert validate_baseline_continuity(item)
    assert item.score == 100
    assert item.state == "BASELINE_CONTINUITY_READY"
    assert baseline_continuity_to_dict(item)["read_only"] is True


def test_phase72():
    item = build_integrity_reconciliation(
        expected_digest="abc123"
    )
    assert validate_integrity_reconciliation(item)
    assert item.integrity_match is True
    assert item.score == 100
    assert item.state == "INTEGRITY_RECONCILED"
    assert integrity_to_dict(item)["dry_run"] is True


def test_phase73():
    item = build_final_review()
    assert validate_final_review(item)
    assert item.score == 100
    assert item.state == "FINAL_REVIEW_READY"
    assert item.response_locked is True
    assert item.human_review_required is True
    assert final_review_to_dict(item)["execution_allowed"] is False


def test_phase74():
    item = build_monitoring_readiness()
    assert validate_monitoring_readiness(item)
    assert item.monitoring_ready is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_MONITORING_READY"
    assert monitoring_readiness_to_dict(item)["response_locked"] is True


def test_negative_integrity():
    item = build_integrity_reconciliation(
        expected_digest="abc123",
        observed_digest="different",
    )
    assert validate_integrity_reconciliation(item)
    assert item.integrity_match is False
    assert item.reconciliation_valid is False
    assert item.score == 0


def test_negative_review():
    item = build_final_review(
        audit_ok=False,
    )
    assert validate_final_review(item)
    assert item.review_valid is False
    assert item.score == 0


def test_negative_readiness():
    item = build_monitoring_readiness(
        response_locked=False,
    )
    assert not validate_monitoring_readiness(item)
    assert item.monitoring_ready is False
    assert item.score == 0
