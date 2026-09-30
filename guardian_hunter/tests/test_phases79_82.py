from guardian_hunter.governance.phase79_telemetry_continuity import (
    build_telemetry_continuity,
    telemetry_to_dict,
    validate_telemetry_continuity,
)
from guardian_hunter.verification.phase80_event_reconciliation import (
    build_event_reconciliation,
    event_reconciliation_to_dict,
    validate_event_reconciliation,
)
from guardian_hunter.governance.phase81_monitoring_review import (
    build_monitoring_review,
    monitoring_review_to_dict,
    validate_monitoring_review,
)
from guardian_hunter.governance.phase82_continuous_readiness import (
    build_continuous_readiness,
    continuous_readiness_to_dict,
    validate_continuous_readiness,
)


def test_phase79():
    item = build_telemetry_continuity()
    assert validate_telemetry_continuity(item)
    assert item.continuity_valid is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_TELEMETRY_CONTINUOUS"
    assert telemetry_to_dict(item)["read_only"] is True


def test_phase80():
    item = build_event_reconciliation()
    assert validate_event_reconciliation(item)
    assert item.count_match is True
    assert item.digest_match is True
    assert item.reconciliation_valid is True
    assert item.score == 100
    assert item.state == "EVENTS_RECONCILED"
    assert event_reconciliation_to_dict(item)["dry_run"] is True


def test_phase81():
    item = build_monitoring_review()
    assert validate_monitoring_review(item)
    assert item.review_valid is True
    assert item.score == 100
    assert item.state == "MONITORING_REVIEW_READY"
    assert item.response_locked is True
    assert item.human_review_required is True
    assert monitoring_review_to_dict(item)["execution_allowed"] is False


def test_phase82():
    item = build_continuous_readiness()
    assert validate_continuous_readiness(item)
    assert item.continuous_ready is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_CONTINUOUS_READY"
    assert item.response_locked is True
    assert continuous_readiness_to_dict(item)["read_only"] is True


def test_negative_telemetry():
    item = build_telemetry_continuity(
        telemetry_integrity_ok=False,
    )
    assert validate_telemetry_continuity(item)
    assert item.continuity_valid is False
    assert item.score == 0


def test_negative_events():
    item = build_event_reconciliation(
        expected_event_count=3,
        observed_event_count=2,
    )
    assert validate_event_reconciliation(item)
    assert item.count_match is False
    assert item.reconciliation_valid is False
    assert item.score == 0


def test_negative_monitoring_review():
    item = build_monitoring_review(
        audit_ready=False,
    )
    assert validate_monitoring_review(item)
    assert item.review_valid is False
    assert item.score == 0


def test_negative_continuous():
    item = build_continuous_readiness(
        observability_ready=False,
    )
    assert validate_continuous_readiness(item)
    assert item.continuous_ready is False
    assert item.score == 0
