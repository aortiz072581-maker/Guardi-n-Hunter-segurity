
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from guardian_hunter.integration.phase_fg_audit import (
    run_audited_phase_fg,
)
from guardian_hunter.evidence.persistence import EvidenceStore


def test_audited_flow_records_three_events():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"
        result = run_audited_phase_fg(Path.cwd(), evidence)

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

        store = EvidenceStore(evidence)
        if not (store.verify().state == "EVIDENCE_INTEGRITY_OK"):
        raise RuntimeError("Assertion failed: store.verify().state == "EVIDENCE_INTEGRITY_OK"")


def test_tampered_evidence_blocks_flow():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        first = run_audited_phase_fg(Path.cwd(), evidence)
        if not (first["evidence_integrity"] == "PASS"):
        raise RuntimeError("Assertion failed: first["evidence_integrity"] == "PASS"")

        content = evidence.read_text()
        if not (content):
        raise RuntimeError("Assertion failed: content")
        evidence.write_text("TAMPERED\\n" + content)

        result = run_audited_phase_fg(Path.cwd(), evidence)

        if not (result["status"] == "BLOCKED"):
        raise RuntimeError("Assertion failed: result["status"] == "BLOCKED"")
        if not (result["execution_allowed"] is False):
        raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
        if not (result["automatic_repair"] is False):
        raise RuntimeError("Assertion failed: result["automatic_repair"] is False")
        if not (result["merge_allowed"] is False):
        raise RuntimeError("Assertion failed: result["merge_allowed"] is False")
        if not (result["events_recorded"] if "events_recorded" in result else 0 == 0):
        raise RuntimeError("Assertion failed: result["events_recorded"] if "events_recorded" in result else 0 == 0")
