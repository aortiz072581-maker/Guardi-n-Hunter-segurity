from pathlib import Path

from guardian_hunter.tamper.detection import (
    TamperSeverity,
    TamperSignal,
    assess_tamper,
    build_file_baseline,
    compare_file_digest,
    detect_authorization_anomaly,
    detect_configuration_drift,
    detect_evidence_chain_anomaly,
    detect_file_integrity_drift,
    detect_repeated_failures,
    detect_safety_state,
    fail_closed,
    safety_invariants_hold,
)


def test_safety_invariants():
    assert safety_invariants_hold()


def test_file_baseline_clean(tmp_path: Path):
    target = tmp_path / "sample.txt"
    target.write_text("trusted", encoding="utf-8")

    baseline = build_file_baseline((target,))

    findings = detect_file_integrity_drift(baseline)

    assert findings == ()


def test_file_modification_is_detected(tmp_path: Path):
    target = tmp_path / "sample.txt"
    target.write_text("trusted", encoding="utf-8")

    baseline = build_file_baseline((target,))

    target.write_text("modified", encoding="utf-8")

    findings = detect_file_integrity_drift(baseline)

    assert len(findings) == 1
    assert findings[0].signal == TamperSignal.FILE_INTEGRITY_DRIFT
    assert findings[0].severity == TamperSeverity.HIGH


def test_missing_file_is_detected(tmp_path: Path):
    target = tmp_path / "missing.txt"

    finding = compare_file_digest(
        target,
        "a" * 64,
    )

    assert finding is not None
    assert finding.severity == TamperSeverity.CRITICAL


def test_safety_state_drift_is_critical():
    finding = detect_safety_state(
        {
            "READ_ONLY": True,
            "DRY_RUN": True,
            "REAL_EXECUTION_BLOCKED": False,
            "HUMAN_REVIEW_REQUIRED": True,
            "RESPONSE_LOCKED": True,
        }
    )

    assert finding is not None
    assert finding.signal == TamperSignal.SAFETY_STATE_DRIFT
    assert finding.severity == TamperSeverity.CRITICAL


def test_authorization_execution_anomaly_is_critical():
    finding = detect_authorization_anomaly(
        authorized=True,
        execution_allowed=True,
        human_review_required=True,
    )

    assert finding is not None
    assert finding.signal == TamperSignal.AUTHORIZATION_ANOMALY
    assert finding.severity == TamperSeverity.CRITICAL


def test_evidence_chain_anomaly_is_detected():
    finding = detect_evidence_chain_anomaly(
        valid=False,
        records=4,
        invalid_hash=True,
        invalid_chain=False,
    )

    assert finding is not None
    assert finding.signal == TamperSignal.EVIDENCE_CHAIN_ANOMALY
    assert finding.severity == TamperSeverity.CRITICAL


def test_repeated_failures_are_detected():
    finding = detect_repeated_failures(
        failure_count=3,
        threshold=3,
    )

    assert finding is not None
    assert finding.signal == TamperSignal.REPEATED_FAILURES


def test_configuration_drift_is_detected():
    finding = detect_configuration_drift(
        expected={
            "mode": "DRY_RUN",
            "locked": True,
        },
        actual={
            "mode": "DRY_RUN",
            "locked": False,
        },
    )

    assert finding is not None
    assert finding.signal == TamperSignal.CONFIGURATION_DRIFT


def test_clean_assessment_remains_fail_closed():
    assessment = assess_tamper(
        target="controlled-target",
        findings=(),
    )

    assert assessment.execution_allowed is False
    assert assessment.response_locked is True
    assert assessment.human_review_required is True
    assert fail_closed(assessment)


def test_tamper_assessment_remains_fail_closed():
    finding = detect_repeated_failures(
        failure_count=6,
        threshold=3,
    )

    assessment = assess_tamper(
        target="controlled-target",
        findings=(finding,),
    )

    assert assessment.risk_level == TamperSeverity.CRITICAL
    assert assessment.execution_allowed is False
    assert fail_closed(assessment)
