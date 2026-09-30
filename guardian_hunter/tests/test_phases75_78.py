from guardian_hunter.governance.phase75_evidence_readiness import (
    build_evidence_readiness,
    evidence_readiness_to_dict,
    validate_evidence_readiness,
)
from guardian_hunter.verification.phase76_alert_reconciliation import (
    build_alert_reconciliation,
    alert_reconciliation_to_dict,
    validate_alert_reconciliation,
)
from guardian_hunter.governance.phase77_incident_review import (
    build_incident_review,
    incident_review_to_dict,
    validate_incident_review,
)
from guardian_hunter.governance.phase78_observability import (
    build_observability_readiness,
    observability_to_dict,
    validate_observability_readiness,
)


def test_phase75():
    item = build_evidence_readiness()
    assert validate_evidence_readiness(item)
    assert item.evidence_ready is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_EVIDENCE_READY"
    assert evidence_readiness_to_dict(item)["read_only"] is True


def test_phase76():
    item = build_alert_reconciliation()
    assert validate_alert_reconciliation(item)
    assert item.count_match is True
    assert item.digest_match is True
    assert item.reconciliation_valid is True
    assert item.score == 100
    assert item.state == "ALERTS_RECONCILED"
    assert alert_reconciliation_to_dict(item)["dry_run"] is True


def test_phase77():
    item = build_incident_review()
    assert validate_incident_review(item)
    assert item.review_valid is True
    assert item.score == 100
    assert item.state == "INCIDENT_REVIEW_READY"
    assert item.response_locked is True
    assert item.human_review_required is True
    assert incident_review_to_dict(item)["execution_allowed"] is False


def test_phase78():
    item = build_observability_readiness()
    assert validate_observability_readiness(item)
    assert item.observability_ready is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_OBSERVABILITY_READY"
    assert item.response_locked is True
    assert observability_to_dict(item)["read_only"] is True


def test_negative_evidence():
    item = build_evidence_readiness(
        evidence_integrity_ok=False,
    )
    assert validate_evidence_readiness(item)
    assert item.evidence_ready is False
    assert item.score == 0


def test_negative_alerts():
    item = build_alert_reconciliation(
        expected_alert_count=2,
        observed_alert_count=1,
    )
    assert validate_alert_reconciliation(item)
    assert item.count_match is False
    assert item.reconciliation_valid is False
    assert item.score == 0


def test_negative_incident_review():
    item = build_incident_review(
        audit_ready=False,
    )
    assert validate_incident_review(item)
    assert item.review_valid is False
    assert item.score == 0


def test_negative_observability():
    item = build_observability_readiness(
        monitoring_ready=False,
    )
    assert validate_observability_readiness(item)
    assert item.observability_ready is False
    assert item.score == 0
