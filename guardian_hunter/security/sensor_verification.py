"""Offline security checks for sensor evidence integration."""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.integration.security_sensor_evidence import (
    persist_sensor_assessment,
)


def verify_sensor_evidence() -> bool:
    report = {
        "schema": "guardian-security-sensors-v1",
        "states": {
            "gitleaks": "CLEAN",
            "osv": "FINDINGS",
        },
        "finding_count": 1,
        "findings": [{"id": "GH-OSV-000001"}],
        "assessment_complete": True,
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    report["sha256"] = hashlib.sha256(
        json.dumps(
            report,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    with TemporaryDirectory(prefix="gh-sensor-verify-") as tmp:
        path = Path(tmp) / "evidence.jsonl"

        saved = persist_sensor_assessment(report, path)

        if saved["state"] != "PERSISTED_AND_VERIFIED":
            return False

        altered = dict(report)
        altered["finding_count"] = 2

        try:
            persist_sensor_assessment(altered, path)
        except ValueError as exc:
            if str(exc) != "SENSOR_REPORT_HASH_MISMATCH":
                return False
        else:
            return False

        entry = json.loads(path.read_text())
        entry["payload"]["finding_count"] = 999
        path.write_text(json.dumps(entry) + "\n")

        before = path.read_bytes()

        try:
            persist_sensor_assessment(report, path)
        except RuntimeError as exc:
            if str(exc) != "EVIDENCE_CHAIN_COMPROMISED":
                return False
        else:
            return False

        if path.read_bytes() != before:
            return False

        return (
            EvidenceStore(path).verify().state
            != "EVIDENCE_INTEGRITY_OK"
        )
