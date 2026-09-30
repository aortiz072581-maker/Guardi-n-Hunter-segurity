"""Phase 72 — Defensive Integrity Reconciliation.

Reconciles integrity inputs without modifying the underlying data.
"""

from dataclasses import dataclass
from hashlib import sha256
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class IntegrityReconciliation:
    expected_digest: str
    observed_digest: str
    integrity_match: bool
    reconciliation_valid: bool
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


def build_integrity_reconciliation(
    expected_digest,
    observed_digest=None,
):
    if observed_digest is None:
        observed_digest = expected_digest

    integrity_match = bool(
        expected_digest
        and observed_digest
        and expected_digest == observed_digest
    )

    reconciliation_valid = bool(
        integrity_match
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if reconciliation_valid else 0

    state = (
        "INTEGRITY_RECONCILED"
        if reconciliation_valid
        else "INTEGRITY_RECONCILIATION_BLOCKED"
    )

    return IntegrityReconciliation(
        expected_digest=expected_digest,
        observed_digest=observed_digest,
        integrity_match=integrity_match,
        reconciliation_valid=reconciliation_valid,
        score=score,
        state=state,
    )


def integrity_to_dict(record):
    return {
        "expected_digest": record.expected_digest,
        "observed_digest": record.observed_digest,
        "integrity_match": record.integrity_match,
        "reconciliation_valid": record.reconciliation_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_integrity_reconciliation(record):
    if not isinstance(record, IntegrityReconciliation):
        return False
    if not record.expected_digest:
        return False
    if not record.observed_digest:
        return False
    if record.integrity_match != (
        record.expected_digest == record.observed_digest
    ):
        return False
    if record.reconciliation_valid and record.score != 100:
        return False
    if not record.read_only:
        return False
    if not record.dry_run:
        return False
    if record.execution_allowed:
        return False
    return True
