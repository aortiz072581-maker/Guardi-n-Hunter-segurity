"""Phase 84 — Defensive Correlation Reconciliation."""

from dataclasses import dataclass
from hashlib import sha256
import json


READ_ONLY = True
DRY_RUN = True
EXECUTION_ALLOWED = False


@dataclass(frozen=True)
class DefensiveCorrelationReconciliation:
    expected_signal_count: int
    observed_signal_count: int
    expected_digest: str
    observed_digest: str
    count_match: bool
    digest_match: bool
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


def build_correlation_reconciliation(
    expected_signal_count=0,
    observed_signal_count=None,
    expected_digest=None,
    observed_digest=None,
):
    if observed_signal_count is None:
        observed_signal_count = expected_signal_count

    if expected_digest is None:
        expected_digest = _digest({
            "signal_count": expected_signal_count,
        })

    if observed_digest is None:
        observed_digest = expected_digest

    count_match = (
        int(expected_signal_count) == int(observed_signal_count)
    )

    digest_match = (
        bool(expected_digest)
        and bool(observed_digest)
        and expected_digest == observed_digest
    )

    reconciliation_valid = bool(
        count_match
        and digest_match
        and READ_ONLY
        and DRY_RUN
        and not EXECUTION_ALLOWED
    )

    score = 100 if reconciliation_valid else 0

    state = (
        "CORRELATION_RECONCILED"
        if reconciliation_valid
        else "CORRELATION_RECONCILIATION_BLOCKED"
    )

    return DefensiveCorrelationReconciliation(
        expected_signal_count=int(expected_signal_count),
        observed_signal_count=int(observed_signal_count),
        expected_digest=expected_digest,
        observed_digest=observed_digest,
        count_match=count_match,
        digest_match=digest_match,
        reconciliation_valid=reconciliation_valid,
        score=score,
        state=state,
    )


def correlation_to_dict(record):
    return {
        "expected_signal_count": record.expected_signal_count,
        "observed_signal_count": record.observed_signal_count,
        "expected_digest": record.expected_digest,
        "observed_digest": record.observed_digest,
        "count_match": record.count_match,
        "digest_match": record.digest_match,
        "reconciliation_valid": record.reconciliation_valid,
        "score": record.score,
        "state": record.state,
        "read_only": record.read_only,
        "dry_run": record.dry_run,
        "execution_allowed": record.execution_allowed,
    }


def validate_correlation_reconciliation(record):
    if not isinstance(record, DefensiveCorrelationReconciliation):
        return False
    if record.expected_signal_count < 0:
        return False
    if record.observed_signal_count < 0:
        return False
    if record.count_match != (
        record.expected_signal_count == record.observed_signal_count
    ):
        return False
    if record.digest_match != (
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
