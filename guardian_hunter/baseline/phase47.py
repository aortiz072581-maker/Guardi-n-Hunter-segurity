"""Phase 47 — Defensive Baseline Integrity."""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class BaselineRecord:
    baseline_id: str
    values: dict
    digest: str
    execution_allowed: bool = False


def _digest(values: dict) -> str:
    canonical = repr(sorted(values.items())).encode("utf-8")
    return sha256(canonical).hexdigest()


def create_baseline(baseline_id: str, values: dict) -> BaselineRecord:
    return BaselineRecord(
        baseline_id=baseline_id,
        values=dict(values),
        digest=_digest(values),
        execution_allowed=False,
    )


def verify_baseline(baseline: BaselineRecord) -> bool:
    return (
        baseline.execution_allowed is False
        and baseline.digest == _digest(baseline.values)
    )


def compare_baseline(
    baseline: BaselineRecord,
    current_values: dict,
) -> dict:
    expected = baseline.values
    current = dict(current_values)

    added = sorted(set(current) - set(expected))
    removed = sorted(set(expected) - set(current))
    changed = sorted(
        key
        for key in set(expected) & set(current)
        if expected[key] != current[key]
    )

    return {
        "phase": 47,
        "baseline_id": baseline.baseline_id,
        "integrity": verify_baseline(baseline),
        "added": added,
        "removed": removed,
        "changed": changed,
        "changed_count": len(added) + len(removed) + len(changed),
        "execution_allowed": False,
    }


def build_baseline_report(baseline: BaselineRecord) -> dict:
    return {
        "phase": 47,
        "baseline_id": baseline.baseline_id,
        "digest": baseline.digest,
        "integrity": verify_baseline(baseline),
        "execution_allowed": False,
    }
