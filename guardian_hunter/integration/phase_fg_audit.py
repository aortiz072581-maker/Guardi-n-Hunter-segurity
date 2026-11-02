
"""Audited D-G defensive flow. No automatic execution."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from time import time

from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.integration.phase_de import (
    run_phase_de, build_defensive_response
)
from guardian_hunter.integration.phase_fg import prepare_phase_fg

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False

def run_audited_phase_fg(root, evidence_path):
    result = {
        "status": "BLOCKED",
        "reason": "NOT_VERIFIED",
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    try:
        store = EvidenceStore(Path(evidence_path))

        if store.verify().state != "EVIDENCE_INTEGRITY_OK":
            result["reason"] = "EVIDENCE_TAMPER"
            return result

        assessment = run_phase_de(Path(root))
        response = build_defensive_response(assessment)
        recovery = prepare_phase_fg(assessment)

        for name, data in (
            ("PHASE_DE_ASSESSMENT", assessment),
            ("PHASE_DE_RESPONSE", response),
            ("PHASE_FG_RECOVERY", recovery),
        ):
            store.append(
                evidence_id=str(uuid4()),
                event_type=name,
                timestamp=time(),
                payload={
                    "schema": data.get("schema"),
                    "status": data.get("status"),
                    "reason": data.get("reason"),
                    "execution_allowed": False,
                    "automatic_repair": False,
                    "merge_allowed": False,
                    "human_approval_required": True,
                },
            )

        if store.verify().state != "EVIDENCE_INTEGRITY_OK":
            result["reason"] = "EVIDENCE_VERIFY_FAILED"
            return result

        result["status"] = recovery.get("status", "BLOCKED")
        result["reason"] = recovery.get("reason")
        result["evidence_integrity"] = "PASS"
        result["events_recorded"] = 3
        return result

    except Exception as exc:
        result["reason"] = "AUDIT_FAILURE"
        result["error_type"] = type(exc).__name__
        return result
