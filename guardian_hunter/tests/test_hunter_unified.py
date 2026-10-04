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

    assert report["execution_allowed"] is False
    assert report["automatic_commit"] is False
    assert report["automatic_baseline_update"] is False
    assert report["human_approval_required"] is True


def test_hunter_uses_integrity_baseline_not_git_trust_baseline():
    source = Path(hunter.__file__).read_text(encoding="utf-8")

    assert '"data" / "integrity_baseline.json"' in source
    assert (
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

    assert hunter.main() == 0


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

    assert hunter.main() == 1
