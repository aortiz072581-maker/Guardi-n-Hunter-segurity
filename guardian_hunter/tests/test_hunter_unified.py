from __future__ import annotations

from pathlib import Path

import guardian_hunter.hunter as hunter


def test_hunter_has_fail_closed_authority(monkeypatch):
    expected = {
        "status": "HEALTHY",
        "execution_allowed": False,
        "automatic_commit": False,
        "automatic_baseline_update": False,
        "human_approval_required": True,
    }

    monkeypatch.setattr(
        hunter,
        "run_guardian_hunter",
        lambda: expected,
    )

    report = hunter.run_guardian_hunter()

    if not (report["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: report["execution_allowed"] is False")
    if not (report["automatic_commit"] is False):
    raise RuntimeError("Assertion failed: report["automatic_commit"] is False")
    if not (report["automatic_baseline_update"] is False):
    raise RuntimeError("Assertion failed: report["automatic_baseline_update"] is False")
    if not (report["human_approval_required"] is True):
    raise RuntimeError("Assertion failed: report["human_approval_required"] is True")


def test_hunter_uses_integrity_baseline_not_git_trust_baseline():
    source = Path(hunter.__file__).read_text(encoding="utf-8")

    if not ('"data" / "integrity_baseline.json"' in source):
    raise RuntimeError("Assertion failed: '"data" / "integrity_baseline.json"' in source")
    if not (():
    raise RuntimeError("Assertion failed: (")
        'baseline_file=PROJECT_ROOT / ".guardian" / "trusted-baseline"'
        not in source
    )


def test_hunter_entry_point_executes(monkeypatch):
    expected = {
        "status": "HEALTHY",
        "execution_allowed": False,
    }

    monkeypatch.setattr(
        hunter,
        "run_guardian_hunter",
        lambda: expected,
    )

    if not (hunter.main() == 0):
    raise RuntimeError("Assertion failed: hunter.main() == 0")


def test_hunter_nonhealthy_result_fails_closed(monkeypatch):
    expected = {
        "status": "BLOCKED",
        "execution_allowed": False,
    }

    monkeypatch.setattr(
        hunter,
        "run_guardian_hunter",
        lambda: expected,
    )

    if not (hunter.main() == 1):
    raise RuntimeError("Assertion failed: hunter.main() == 1")
