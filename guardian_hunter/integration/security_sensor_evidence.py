"""Persist verified sensor summaries without privileged actions."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from guardian_hunter.evidence.persistence import EvidenceStore


def persist_sensor_assessment(
    report: dict,
    evidence_path: str | Path,
) -> dict:
    if not isinstance(report, dict):
        raise ValueError("INVALID_SENSOR_REPORT")

    payload = {
        key: value
        for key, value in report.items()
        if key != "sha256"
    }

    digest = hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()

    if digest != report.get("sha256"):
        raise ValueError("SENSOR_REPORT_HASH_MISMATCH")

    if report.get("assessment_complete") is not True:
        raise PermissionError("INCOMPLETE_ASSESSMENT_DENIED")

    states = report.get("states")

    if (
        not isinstance(states, dict)
        or set(states) != {"gitleaks", "osv"}
        or any(
            state not in {"CLEAN", "FINDINGS"}
            for state in states.values()
        )
    ):
        raise ValueError("INVALID_SENSOR_STATES")

    if (
        report.get("execution_allowed") is not False
        or report.get("automatic_repair") is not False
        or report.get("merge_allowed") is not False
        or report.get("human_approval_required") is not True
    ):
        raise PermissionError("SENSOR_AUTHORITY_DENIED")

    count = report.get("finding_count")

    if (
        type(count) is not int
        or count < 0
        or not isinstance(report.get("findings"), list)
        or count != len(report["findings"])
    ):
        raise ValueError("INVALID_FINDING_COUNT")

    store = EvidenceStore(Path(evidence_path))

    if store.verify().state != "EVIDENCE_INTEGRITY_OK":
        raise RuntimeError("EVIDENCE_CHAIN_COMPROMISED")

    record = store.append(
        evidence_id=f"sensor-{digest[:24]}",
        event_type="SECURITY_SENSOR_ASSESSMENT",
        timestamp=time.time(),
        payload={
            "schema": "guardian-security-sensors-v1",
            "report_sha256": digest,
            "finding_count": count,
            "states": dict(states),
            "assessment_complete": True,
            "execution_allowed": False,
            "automatic_repair": False,
            "merge_allowed": False,
            "human_approval_required": True,
        },
    )

    if store.verify().state != "EVIDENCE_INTEGRITY_OK":
        raise RuntimeError("EVIDENCE_POSTWRITE_VERIFY_FAILED")

    return {
        "evidence_id": record.evidence_id,
        "record_hash": record.record_hash,
        "sequence": record.sequence,
        "state": "PERSISTED_AND_VERIFIED",
        "execution_allowed": False,
    }
