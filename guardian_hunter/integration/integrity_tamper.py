"""Read-only integrity and tamper integration."""

import json
from pathlib import Path

from guardian_hunter.integrity.self_integrity import (
    fail_closed as integrity_fail_closed,
    verify_records,
)
from guardian_hunter.tamper.detection import (
    assess_tamper,
    assessment_to_dict,
    detect_safety_state,
    fail_closed as tamper_fail_closed,
)


def inspect_integrity_tamper(
    baseline_file: Path,
    root: Path,
) -> dict:
    baseline = json.loads(baseline_file.read_text())
    integrity = verify_records(root, baseline)

    finding = detect_safety_state({
        "READ_ONLY": True,
        "DRY_RUN": True,
        "REAL_EXECUTION_BLOCKED": True,
        "HUMAN_REVIEW_REQUIRED": True,
        "RESPONSE_LOCKED": True,
    })

    findings = () if finding is None else (finding,)
    tamper = assess_tamper(
        target="guardian-hunter",
        findings=findings,
    )

    return {
        "integrity_state": integrity.state,
        "integrity_fail_closed": integrity_fail_closed(integrity),
        "added": integrity.added,
        "modified": integrity.modified,
        "deleted": integrity.deleted,
        "unchanged": integrity.unchanged,
        "tamper": assessment_to_dict(tamper),
        "tamper_fail_closed": tamper_fail_closed(tamper),
        "execution_allowed": False,
        "response_locked": True,
    }
