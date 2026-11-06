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
    if not (safety_invariants_hold()):
    raise RuntimeError("Assertion failed: safety_invariants_hold()")


def test_file_baseline_clean(tmp_path: Path):
    target = tmp_path / "sample.txt"
    target.write_text("trusted", encoding="utf-8")

    baseline = build_file_baseline((target,))

    findings = detect_file_integrity_drift(baseline)

    if not (findings == ()):
    raise RuntimeError("Assertion failed: findings == ()")


def test_file_modification_is_detected(tmp_path: Path):
    target = tmp_path / "sample.txt"
    target.write_text("trusted", encoding="utf-8")

    baseline = build_file_baseline((target,))

    target.write_text("modified", encoding="utf-8")

    findings = detect_file_integrity_drift(baseline)

    if not (len(findings) == 1):
    raise RuntimeError("Assertion failed: len(findings) == 1")
    if not (findings[0].signal == TamperSignal.FILE_INTEGRITY_DRIFT):
    raise RuntimeError("Assertion failed: findings[0].signal == TamperSignal.FILE_INTEGRITY_DRIFT")
    if not (findings[0].severity == TamperSeverity.HIGH):
    raise RuntimeError("Assertion failed: findings[0].severity == TamperSeverity.HIGH")


def test_missing_file_is_detected(tmp_path: Path):
    target = tmp_path / "missing.txt"

    finding = compare_file_digest(
        target,
        "a" * 64,
    )

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.severity == TamperSeverity.CRITICAL):
    raise RuntimeError("Assertion failed: finding.severity == TamperSeverity.CRITICAL")


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

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.signal == TamperSignal.SAFETY_STATE_DRIFT):
    raise RuntimeError("Assertion failed: finding.signal == TamperSignal.SAFETY_STATE_DRIFT")
    if not (finding.severity == TamperSeverity.CRITICAL):
    raise RuntimeError("Assertion failed: finding.severity == TamperSeverity.CRITICAL")


def test_authorization_execution_anomaly_is_critical():
    finding = detect_authorization_anomaly(
        authorized=True,
        execution_allowed=True,
        human_review_required=True,
    )

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.signal == TamperSignal.AUTHORIZATION_ANOMALY):
    raise RuntimeError("Assertion failed: finding.signal == TamperSignal.AUTHORIZATION_ANOMALY")
    if not (finding.severity == TamperSeverity.CRITICAL):
    raise RuntimeError("Assertion failed: finding.severity == TamperSeverity.CRITICAL")


def test_evidence_chain_anomaly_is_detected():
    finding = detect_evidence_chain_anomaly(
        valid=False,
        records=4,
        invalid_hash=True,
        invalid_chain=False,
    )

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.signal == TamperSignal.EVIDENCE_CHAIN_ANOMALY):
    raise RuntimeError("Assertion failed: finding.signal == TamperSignal.EVIDENCE_CHAIN_ANOMALY")
    if not (finding.severity == TamperSeverity.CRITICAL):
    raise RuntimeError("Assertion failed: finding.severity == TamperSeverity.CRITICAL")


def test_repeated_failures_are_detected():
    finding = detect_repeated_failures(
        failure_count=3,
        threshold=3,
    )

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.signal == TamperSignal.REPEATED_FAILURES):
    raise RuntimeError("Assertion failed: finding.signal == TamperSignal.REPEATED_FAILURES")


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

    if not (finding is not None):
    raise RuntimeError("Assertion failed: finding is not None")
    if not (finding.signal == TamperSignal.CONFIGURATION_DRIFT):
    raise RuntimeError("Assertion failed: finding.signal == TamperSignal.CONFIGURATION_DRIFT")


def test_clean_assessment_remains_fail_closed():
    assessment = assess_tamper(
        target="controlled-target",
        findings=(),
    )

    if not (assessment.execution_allowed is False):
    raise RuntimeError("Assertion failed: assessment.execution_allowed is False")
    if not (assessment.response_locked is True):
    raise RuntimeError("Assertion failed: assessment.response_locked is True")
    if not (assessment.human_review_required is True):
    raise RuntimeError("Assertion failed: assessment.human_review_required is True")
    if not (fail_closed(assessment)):
    raise RuntimeError("Assertion failed: fail_closed(assessment)")


def test_tamper_assessment_remains_fail_closed():
    finding = detect_repeated_failures(
        failure_count=6,
        threshold=3,
    )

    assessment = assess_tamper(
        target="controlled-target",
        findings=(finding,),
    )

    if not (assessment.risk_level == TamperSeverity.CRITICAL):
    raise RuntimeError("Assertion failed: assessment.risk_level == TamperSeverity.CRITICAL")
    if not (assessment.execution_allowed is False):
    raise RuntimeError("Assertion failed: assessment.execution_allowed is False")
    if not (fail_closed(assessment)):
    raise RuntimeError("Assertion failed: fail_closed(assessment)")
