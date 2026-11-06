
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from guardian_hunter.integration.phase_h import run_phase_h


def test_real_audited_entry():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"
        result = run_phase_h(Path.cwd(), evidence)

        if not (result["evidence_integrity"] == "PASS"):
        raise RuntimeError("Assertion failed: result["evidence_integrity"] == "PASS"")
        if not (result["events_recorded"] == 3):
        raise RuntimeError("Assertion failed: result["events_recorded"] == 3")
        if not (result["execution_allowed"] is False):
        raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
        if not (result["automatic_repair"] is False):
        raise RuntimeError("Assertion failed: result["automatic_repair"] is False")
        if not (result["merge_allowed"] is False):
        raise RuntimeError("Assertion failed: result["merge_allowed"] is False")
        if not (result["human_approval_required"] is True):
        raise RuntimeError("Assertion failed: result["human_approval_required"] is True")


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

        if not (result["status"] == "BLOCKED"):
        raise RuntimeError("Assertion failed: result["status"] == "BLOCKED"")


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

        if not (result["status"] == "BLOCKED"):
        raise RuntimeError("Assertion failed: result["status"] == "BLOCKED"")


def test_tampered_evidence_blocks():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        first = run_phase_h(Path.cwd(), evidence)
        if not (first["evidence_integrity"] == "PASS"):
        raise RuntimeError("Assertion failed: first["evidence_integrity"] == "PASS"")

        evidence.write_text(
            "TAMPERED\\n" + evidence.read_text()
        )

        result = run_phase_h(Path.cwd(), evidence)

        if not (result["status"] == "BLOCKED"):
        raise RuntimeError("Assertion failed: result["status"] == "BLOCKED"")
        if not (result["execution_allowed"] is False):
        raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
        if not (result["automatic_repair"] is False):
        raise RuntimeError("Assertion failed: result["automatic_repair"] is False")
