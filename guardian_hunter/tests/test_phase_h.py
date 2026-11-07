
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from guardian_hunter.integration.phase_h import run_phase_h


def test_real_audited_entry():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"
        result = run_phase_h(Path.cwd(), evidence)

        assert result["evidence_integrity"] == "PASS"
        assert result["events_recorded"] == 3
        assert result["execution_allowed"] is False
        assert result["automatic_repair"] is False
        assert result["merge_allowed"] is False
        assert result["human_approval_required"] is True


def test_audit_failure_blocks():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        with patch(
            "guardian_hunter.integration.phase_h.run_audited_phase_fg",
            return_value={
                "status": "MONITORING",
                "execution_allowed": False,
                "automatic_repair": False,
                "merge_allowed": False,
                "human_approval_required": True,
                "evidence_integrity": "FAIL",
                "events_recorded": 3,
            },
        ):
            result = run_phase_h(Path.cwd(), evidence)

        assert result["status"] == "BLOCKED"


def test_unsafe_authority_blocks():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        with patch(
            "guardian_hunter.integration.phase_h.run_audited_phase_fg",
            return_value={
                "status": "MONITORING",
                "execution_allowed": True,
                "automatic_repair": False,
                "merge_allowed": False,
                "human_approval_required": True,
                "evidence_integrity": "PASS",
                "events_recorded": 3,
            },
        ):
            result = run_phase_h(Path.cwd(), evidence)

        assert result["status"] == "BLOCKED"


def test_tampered_evidence_blocks():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        first = run_phase_h(Path.cwd(), evidence)
        assert first["evidence_integrity"] == "PASS"

        evidence.write_text(
            "TAMPERED\\n" + evidence.read_text()
        )

        result = run_phase_h(Path.cwd(), evidence)

        assert result["status"] == "BLOCKED"
        assert result["execution_allowed"] is False
        assert result["automatic_repair"] is False
