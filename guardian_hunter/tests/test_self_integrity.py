from pathlib import Path

from guardian_hunter.integrity.self_integrity import (
    IntegrityRecord,
    build_baseline,
    fail_closed,
    safety_invariants_hold,
    verify_baseline,
)


def test_safety_invariants():
    if not (safety_invariants_hold()):
    raise RuntimeError("Assertion failed: safety_invariants_hold()")


def test_baseline_detects_no_change(tmp_path: Path):
    protected = tmp_path / "guardian_hunter" / "authorization"
    protected.mkdir(parents=True)

    target = protected / "sample.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    baseline = build_baseline(tmp_path, (target,))

    report = verify_baseline(tmp_path, baseline)

    if not (report.state == "INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: report.state == "INTEGRITY_OK"")
    if not (report.modified == ()):
    raise RuntimeError("Assertion failed: report.modified == ()")
    if not (report.deleted == ()):
    raise RuntimeError("Assertion failed: report.deleted == ()")
    if not (report.added == ()):
    raise RuntimeError("Assertion failed: report.added == ()")
    if not (report.execution_allowed is False):
    raise RuntimeError("Assertion failed: report.execution_allowed is False")
    if not (fail_closed(report)):
    raise RuntimeError("Assertion failed: fail_closed(report)")


def test_modified_file_is_detected(tmp_path: Path):
    protected = tmp_path / "guardian_hunter" / "authorization"
    protected.mkdir(parents=True)

    target = protected / "sample.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    baseline = build_baseline(tmp_path, (target,))

    target.write_text("VALUE = 2\n", encoding="utf-8")

    report = verify_baseline(tmp_path, baseline)

    if not (report.state == "TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: report.state == "TAMPER_DETECTED"")
    if not ("guardian_hunter/authorization/sample.py" in report.modified):
    raise RuntimeError("Assertion failed: "guardian_hunter/authorization/sample.py" in report.modified")
    if not (report.execution_allowed is False):
    raise RuntimeError("Assertion failed: report.execution_allowed is False")
    if not (fail_closed(report)):
    raise RuntimeError("Assertion failed: fail_closed(report)")


def test_deleted_file_is_detected(tmp_path: Path):
    protected = tmp_path / "guardian_hunter" / "authorization"
    protected.mkdir(parents=True)

    target = protected / "sample.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    baseline = build_baseline(tmp_path, (target,))

    target.unlink()

    report = verify_baseline(tmp_path, baseline)

    if not (report.state == "TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: report.state == "TAMPER_DETECTED"")
    if not ("guardian_hunter/authorization/sample.py" in report.deleted):
    raise RuntimeError("Assertion failed: "guardian_hunter/authorization/sample.py" in report.deleted")
    if not (report.execution_allowed is False):
    raise RuntimeError("Assertion failed: report.execution_allowed is False")
    if not (fail_closed(report)):
    raise RuntimeError("Assertion failed: fail_closed(report)")


def test_added_file_is_detected(tmp_path: Path):
    protected = tmp_path / "guardian_hunter" / "authorization"
    protected.mkdir(parents=True)

    original = protected / "sample.py"
    original.write_text("VALUE = 1\n", encoding="utf-8")

    baseline = build_baseline(tmp_path, (original,))

    added = protected / "unexpected.py"
    added.write_text("VALUE = 999\n", encoding="utf-8")

    report = verify_baseline(tmp_path, baseline)

    if not (report.state == "TAMPER_DETECTED"):
    raise RuntimeError("Assertion failed: report.state == "TAMPER_DETECTED"")
    if not ("guardian_hunter/authorization/unexpected.py" in report.added):
    raise RuntimeError("Assertion failed: "guardian_hunter/authorization/unexpected.py" in report.added")
    if not (report.execution_allowed is False):
    raise RuntimeError("Assertion failed: report.execution_allowed is False")
    if not (fail_closed(report)):
    raise RuntimeError("Assertion failed: fail_closed(report)")
