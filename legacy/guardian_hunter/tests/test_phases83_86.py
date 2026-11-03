from guardian_hunter.governance.phase83_signal_continuity import (
    build_signal_continuity,
    signal_to_dict,
    validate_signal_continuity,
)
from guardian_hunter.verification.phase84_correlation_reconciliation import (
    build_correlation_reconciliation,
    correlation_to_dict,
    validate_correlation_reconciliation,
)
from guardian_hunter.governance.phase85_decision_review import (
    build_decision_review,
    decision_review_to_dict,
    validate_decision_review,
)
from guardian_hunter.governance.phase86_decision_continuity import (
    build_decision_continuity,
    decision_continuity_to_dict,
    validate_decision_continuity,
)


def test_phase83():
    item = build_signal_continuity()
    assert validate_signal_continuity(item)
    assert item.continuity_valid is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_SIGNAL_CONTINUOUS"
    assert signal_to_dict(item)["read_only"] is True


def test_phase84():
    item = build_correlation_reconciliation()
    assert validate_correlation_reconciliation(item)
    assert item.count_match is True
    assert item.digest_match is True
    assert item.reconciliation_valid is True
    assert item.score == 100
    assert item.state == "CORRELATION_RECONCILED"
    assert correlation_to_dict(item)["dry_run"] is True


def test_phase85():
    item = build_decision_review()
    assert validate_decision_review(item)
    assert item.review_valid is True
    assert item.score == 100
    assert item.state == "DECISION_REVIEW_READY"
    assert item.response_locked is True
    assert item.human_review_required is True
    assert decision_review_to_dict(item)["execution_allowed"] is False


def test_phase86():
    item = build_decision_continuity()
    assert validate_decision_continuity(item)
    assert item.continuity_ready is True
    assert item.score == 100
    assert item.state == "DEFENSIVE_DECISION_CONTINUOUS"
    assert item.response_locked is True
    assert decision_continuity_to_dict(item)["read_only"] is True


def test_negative_signal():
    item = build_signal_continuity(
        signals_integrity_ok=False,
    )
    assert validate_signal_continuity(item)
    assert item.continuity_valid is False
    assert item.score == 0


def test_negative_correlation():
    item = build_correlation_reconciliation(
        expected_signal_count=4,
        observed_signal_count=3,
    )
    assert validate_correlation_reconciliation(item)
    assert item.count_match is False
    assert item.reconciliation_valid is False
    assert item.score == 0


def test_negative_decision_review():
    item = build_decision_review(
        risk_ready=False,
    )
    assert validate_decision_review(item)
    assert item.review_valid is False
    assert item.score == 0


def test_negative_decision_continuity():
    item = build_decision_continuity(
        decision_review_ready=False,
    )
    assert validate_decision_continuity(item)
    assert item.continuity_ready is False
    assert item.score == 0
