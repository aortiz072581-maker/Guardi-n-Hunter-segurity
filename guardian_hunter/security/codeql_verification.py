
import hashlib
import json
from pathlib import Path

from guardian_hunter.evidence.persistence import EvidenceStore


# TODO audit 8: complejidad 33 - refactorizar cuando resto esté cerrado, no tocar lógica ahora
def verify_codeql_evidence(
    sarif_path=None,
    evidence_path=None,
):
    """Read-only CodeQL SARIF and evidence verification."""

    if sarif_path is None:
        sarif_path = (
            Path.home()
            / "codeql-staging/guardian-codeql-v2.sarif"
        )

    if evidence_path is None:
        evidence_path = Path(
            ".guardian/local-backups/codeql-evidence.jsonl"
        )

    try:
        raw = Path(sarif_path).read_bytes()
        report = json.loads(raw)

        if report.get("version") != "2.1.0":
            return False

        runs = report.get("runs")
        if not isinstance(runs, list) or not runs:
            return False

        results = []

        for run in runs:
            if (
                run.get("tool", {})
                .get("driver", {})
                .get("name") != "CodeQL"
            ):
                return False

            items = run.get("results")
            if not isinstance(items, list):
                return False

            if not all(isinstance(item, dict) for item in items):
                return False

            results.extend(items)

        digest = hashlib.sha256(raw).hexdigest()

        store = EvidenceStore(evidence_path)
        v = store.verify()

        if (
            v.state != "EVIDENCE_INTEGRITY_OK"
            or v.invalid_sequence
            or v.invalid_hash
            or v.invalid_chain
            or v.execution_allowed
            or not v.read_only
            or not v.dry_run
            or not v.real_execution_blocked
            or not v.human_review_required
            or not v.response_locked
        ):
            return False

        matches = [
            record
            for record in store.records()
            if record.event_type == "CODEQL_SARIF_ASSESSMENT"
            and record.payload.get("tool") == "CodeQL"
            and record.payload.get("version") == "2.27.1"
            and record.payload.get("sarif_sha256") == digest
            and record.payload.get("finding_count") == len(results)
            and record.payload.get("source_files") == 463
            and record.payload.get("execution_allowed") is False
            and record.payload.get("automatic_repair") is False
            and record.payload.get("merge_allowed") is False
            and record.payload.get("human_approval_required") is True
        ]

        return len(matches) == 1

    except (OSError, ValueError, TypeError, KeyError):
        return False
