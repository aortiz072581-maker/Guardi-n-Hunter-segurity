
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

        assert result["evidence_integrity"] == "PASS"
        assert result["events_recorded"] == 3
        assert result["execution_allowed"] is False
        assert result["automatic_repair"] is False
        assert result["merge_allowed"] is False

        store = EvidenceStore(evidence)
        assert store.verify().state == "EVIDENCE_INTEGRITY_OK"


def test_tampered_evidence_blocks_flow():
    with TemporaryDirectory() as directory:
        evidence = Path(directory) / "audit.jsonl"

        first = run_audited_phase_fg(Path.cwd(), evidence)
        assert first["evidence_integrity"] == "PASS"

        content = evidence.read_text()
        assert content
        evidence.write_text("TAMPERED\\n" + content)

        result = run_audited_phase_fg(Path.cwd(), evidence)

        assert result["status"] == "BLOCKED"
        assert result["execution_allowed"] is False
        assert result["automatic_repair"] is False
        assert result["merge_allowed"] is False
        assert result["events_recorded"] if "events_recorded" in result else 0 == 0
