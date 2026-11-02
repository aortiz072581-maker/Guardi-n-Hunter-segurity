
"""Guardian Hunter Phase H: audited operational entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from guardian_hunter.integration.phase_fg_audit import (
    run_audited_phase_fg,
)

READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False
AUTOMATIC_REPAIR = False
MERGE_ALLOWED = False
HUMAN_APPROVAL_REQUIRED = True

def run_phase_h(root, evidence_path):
    result = {
        "schema": "guardian-phase-h-v1",
        "status": "BLOCKED",
        "reason": "NOT_VERIFIED",
        "execution_allowed": False,
        "automatic_repair": False,
        "merge_allowed": False,
        "human_approval_required": True,
    }

    try:
        root = Path(root).resolve()
        evidence = Path(evidence_path).resolve()

        if not root.is_dir():
            result["reason"] = "INVALID_ROOT"
            return result

        if evidence.is_symlink():
            result["reason"] = "UNSAFE_EVIDENCE_PATH"
            return result

        assessment = run_audited_phase_fg(root, evidence)

        if not isinstance(assessment, dict):
            result["reason"] = "INVALID_ASSESSMENT"
            return result

        for key in (
            "execution_allowed",
            "automatic_repair",
            "merge_allowed",
        ):
            if assessment.get(key) is not False:
                result["reason"] = "UNSAFE_AUTHORITY"
                return result

        if assessment.get("human_approval_required") is not True:
            result["reason"] = "APPROVAL_REQUIRED"
            return result

        if assessment.get("evidence_integrity") != "PASS":
            result["reason"] = "EVIDENCE_NOT_VERIFIED"
            return result

        if assessment.get("events_recorded") != 3:
            result["reason"] = "INCOMPLETE_AUDIT"
            return result

        status = assessment.get("status")

        if status not in ("MONITORING", "HUMAN_REVIEW_REQUIRED"):
            result["reason"] = "UNSAFE_STATUS"
            return result

        result["status"] = status
        result["reason"] = assessment.get("reason")
        result["evidence_integrity"] = "PASS"
        result["events_recorded"] = 3
        return result

    except Exception as exc:
        result["reason"] = "OPERATIONAL_ERROR"
        result["error_type"] = type(exc).__name__
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Guardian Hunter audited defensive entry point"
    )
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--evidence",
        default=".guardian/phase-h-evidence.jsonl",
    )
    args = parser.parse_args()

    result = run_phase_h(args.root, args.evidence)
    print(json.dumps(result, sort_keys=True))

    return 0 if result["status"] in (
        "MONITORING",
        "HUMAN_REVIEW_REQUIRED",
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
