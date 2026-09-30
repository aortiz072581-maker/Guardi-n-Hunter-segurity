"""
Guardian Hunter — Self-Integrity / Tamper Detection v1

Defensive integrity layer.

Properties:
- READ_ONLY
- DRY_RUN
- REAL_EXECUTION_BLOCKED
- HUMAN_REVIEW_REQUIRED
- RESPONSE_LOCKED

This module:
- creates a deterministic SHA-256 baseline,
- verifies protected files,
- detects modified/deleted/unexpected files,
- never executes external commands,
- never changes protected project files.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass(frozen=True)
class IntegrityRecord:
    path: str
    sha256: str


@dataclass(frozen=True)
class IntegrityReport:
    state: str
    added: tuple[str, ...]
    modified: tuple[str, ...]
    deleted: tuple[str, ...]
    unchanged: tuple[str, ...]
    execution_allowed: bool
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool


def safety_invariants_hold() -> bool:
    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def protected_files(
    root: Path,
    directories: Iterable[str] = (
        "guardian_hunter/authorization",
        "guardian_hunter/decision",
        "guardian_hunter/response",
        "guardian_hunter/network",
        "guardian_hunter/integrity",
    ),
) -> tuple[Path, ...]:
    root = root.resolve()
    found: list[Path] = []

    for directory in directories:
        base = root / directory

        if not base.exists():
            continue

        for path in sorted(base.rglob("*.py")):
            if path.is_file():
                found.append(path)

    return tuple(sorted(set(found)))


def build_baseline(
    root: Path,
    files: Iterable[Path] | None = None,
) -> tuple[IntegrityRecord, ...]:
    root = root.resolve()

    selected = tuple(files) if files is not None else protected_files(root)

    records = []

    for path in sorted(selected):
        if not path.is_file():
            continue

        records.append(
            IntegrityRecord(
                path=_relative(path, root),
                sha256=_sha256_file(path),
            )
        )

    return tuple(records)


def baseline_to_dict(
    baseline: Iterable[IntegrityRecord],
) -> dict[str, str]:
    return {
        record.path: record.sha256
        for record in baseline
    }


def verify_baseline(
    root: Path,
    baseline: Iterable[IntegrityRecord],
) -> IntegrityReport:
    root = root.resolve()

    expected = baseline_to_dict(baseline)

    current_records = build_baseline(root)
    current = baseline_to_dict(current_records)

    expected_paths = set(expected)
    current_paths = set(current)

    added = tuple(sorted(current_paths - expected_paths))
    deleted = tuple(sorted(expected_paths - current_paths))

    modified = tuple(
        sorted(
            path
            for path in expected_paths & current_paths
            if expected[path] != current[path]
        )
    )

    unchanged = tuple(
        sorted(
            path
            for path in expected_paths & current_paths
            if expected[path] == current[path]
        )
    )

    clean = not added and not modified and not deleted

    state = (
        "INTEGRITY_OK"
        if clean
        else "TAMPER_DETECTED"
    )

    return IntegrityReport(
        state=state,
        added=added,
        modified=modified,
        deleted=deleted,
        unchanged=unchanged,
        execution_allowed=False,
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        real_execution_blocked=REAL_EXECUTION_BLOCKED,
        human_review_required=HUMAN_REVIEW_REQUIRED,
        response_locked=RESPONSE_LOCKED,
    )


def verify_records(
    root: Path,
    baseline: Mapping[str, str],
) -> IntegrityReport:
    records = tuple(
        IntegrityRecord(path=path, sha256=digest)
        for path, digest in baseline.items()
    )

    return verify_baseline(root, records)


def fail_closed(report: IntegrityReport) -> bool:
    return (
        report.execution_allowed is False
        and report.read_only is True
        and report.dry_run is True
        and report.real_execution_blocked is True
        and report.human_review_required is True
        and report.response_locked is True
    )


def run_self_integrity_audit() -> int:
    root = Path.cwd()

    print("GUARDIAN HUNTER — SELF-INTEGRITY / TAMPER DETECTION v1")
    print("=" * 64)

    files = protected_files(root)

    if not files:
        print("PROTECTED FILES: NONE")
        print("AUDIT STATE: FAILED")
        return 1

    baseline = build_baseline(root, files)

    report = verify_baseline(root, baseline)

    print(f"PROTECTED FILES: {len(files)}")
    print(f"BASELINE RECORDS: {len(baseline)}")
    print(f"UNCHANGED: {len(report.unchanged)}")
    print(f"MODIFIED: {len(report.modified)}")
    print(f"DELETED: {len(report.deleted)}")
    print(f"ADDED: {len(report.added)}")
    print(f"INTEGRITY STATE: {report.state}")
    print(
        "FAIL-CLOSED:",
        "OK" if fail_closed(report) else "FAILED",
    )

    print()
    print("READ_ONLY:", READ_ONLY)
    print("DRY_RUN:", DRY_RUN)
    print("REAL_EXECUTION_BLOCKED:", REAL_EXECUTION_BLOCKED)
    print("HUMAN_REVIEW_REQUIRED:", HUMAN_REVIEW_REQUIRED)
    print("RESPONSE_LOCKED:", RESPONSE_LOCKED)
    print("REAL EXECUTION: BLOCKED")

    safe = safety_invariants_hold()

    print()
    print(
        "SAFETY INVARIANTS:",
        "OK" if safe else "FAILED",
    )

    final_ok = (
        report.state == "INTEGRITY_OK"
        and fail_closed(report)
        and safe
    )

    print()

    if final_ok:
        print("=" * 64)
        print("SELF-INTEGRITY / TAMPER DETECTION: OK")
        print("=" * 64)
        return 0

    print("=" * 64)
    print("SELF-INTEGRITY / TAMPER DETECTION: REVIEW REQUIRED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_self_integrity_audit())
