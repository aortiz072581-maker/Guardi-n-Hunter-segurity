"""Phase 71 — Defensive Baseline Continuity.

Read-only continuity verification for the defensive baseline.
No system changes, no execution, no remediation.
"""

from dataclasses import dataclass
from hashlib import sha256
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveBaselineContinuity:
    baseline_id: str
    baseline_digest: str
    baseline_valid: bool
    continuity_valid: bool
    score: int
    state: str
    read_only: bool = True
    dry_run: bool = True
    execution_allowed: bool = False


def _canonical(data):
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(data):
    return sha256(_canonical(data).encode()).hexdigest()


def build_baseline_continuity(
    baseline_id="baseline-71",
    baseline_digest=None,
    baseline_valid=True,
):
    if baseline_digest is None:
        baseline_digest = _digest({
            "baseline_id": baseline_id,
            "baseline_valid": baseline_valid,
        })

    continuity_valid = bool(
        baseline_id
        and baseline_digest
        and baseline_valid
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if continuity_valid else 0

    state = (
        "BASELINE_CONTINUITY_READY"
        if continuity_valid
        else "BASELINE_CONTINUITY_BLOCKED"
    )

    return DefensiveBaselineContinuity(
        baseline_id=baseline_id,
        baseline_digest=baseline_digest,
        baseline_valid=bool(baseline_valid),
        continuity_valid=continuity_valid,
        score=score,
        state=state,
    )


def baseline_continuity_to_dict(record):
    return {
        "baseline_id": record.baseline_id,
        "baseline_digest": record.baseline_digest,
        "baseline_valid": record.baseline_valid,
        "continuity_valid": record.continuity_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_baseline_continuity(record):
    if not isinstance(record, DefensiveBaselineContinuity):
        return False
    if record.score not in (0, 100):
        return False
    if record.continuity_valid and record.score != 100:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    if not record.baseline_id:
        return False
    if not record.baseline_digest:
        return False
    return True
