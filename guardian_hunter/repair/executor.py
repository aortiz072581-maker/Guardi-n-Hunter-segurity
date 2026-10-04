"""Supervised repair executor.

Real filesystem modification is possible only for an explicitly constructed
RepairAction. Protected Guardian Hunter boundaries require a valid
HumanApproval. Commit, merge and trusted-baseline mutation are outside this
module's authority.
"""

from __future__ import annotations

import os
import stat
import tempfile
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from guardian_hunter.repair.approval import (
    ApprovalLedger,
    HumanApproval,
    verify_approval,
)
from guardian_hunter.repair.proposal import RepairProposal


PROTECTED_PREFIXES = (
    ".git/",
    ".guardian/",
    "guardian_hunter/security/",
    "guardian_hunter/authorization/",
    "guardian_hunter/integrity/",
    "guardian_hunter/governance/",
    "guardian_hunter/evidence/",
    "guardian_hunter/gate/",
    "guardian_hunter/auditor/",
    "guardian_hunter/repair/",
    "guardian_hunter/runner/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
)

AUTOMATIC_COMMIT = False
AUTOMATIC_MERGE = False
AUTOMATIC_BASELINE_UPDATE = False


@dataclass(frozen=True)
class RepairAction:
    relative_path: str
    expected_sha256: str | None
    replacement: bytes


@dataclass(frozen=True)
class RepairResult:
    applied: bool
    reason: str
    relative_path: str
    before_sha256: str | None = None
    after_sha256: str | None = None
    protected: bool = False
    approval_verified: bool = False


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _normalize_relative(path: str) -> str:
    raw = path.replace("\\", "/")

    if (
        not raw
        or raw.startswith("/")
        or raw.startswith("./")
        or "\x00" in raw
    ):
        raise ValueError("INVALID_REPAIR_PATH")

    parts = raw.split("/")

    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("INVALID_REPAIR_PATH")

    return "/".join(parts)


def _protected(relative_path: str) -> bool:
    return any(
        relative_path == prefix.rstrip("/")
        or relative_path.startswith(prefix)
        for prefix in PROTECTED_PREFIXES
    )


def _resolve_target(root: Path, relative_path: str) -> Path:
    root = root.resolve(strict=True)
    relative_path = _normalize_relative(relative_path)

    current = root

    for part in relative_path.split("/")[:-1]:
        current = current / part

        if current.is_symlink():
            raise RuntimeError("REPAIR_PATH_SYMLINK")

    target = root / relative_path

    if target.is_symlink():
        raise RuntimeError("REPAIR_TARGET_SYMLINK")

    parent = target.parent.resolve(strict=True)

    try:
        parent.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("REPAIR_PATH_ESCAPE") from exc

    return target


def _atomic_replace(target: Path, content: bytes) -> None:
    parent = target.parent

    fd, temporary_name = tempfile.mkstemp(
        prefix=".guardian-repair-",
        dir=parent,
    )

    temporary = Path(temporary_name)

    try:
        os.fchmod(fd, 0o600)

        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        if temporary.is_symlink():
            raise RuntimeError("REPAIR_TEMP_SYMLINK")

        os.replace(temporary, target)

        directory_fd = os.open(
            parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def apply_repair(
    *,
    root: Path,
    proposal: RepairProposal,
    action: RepairAction,
    baseline: str,
    approval: HumanApproval | None = None,
    approval_ledger: ApprovalLedger | None = None,
) -> RepairResult:
    """Apply one exact supervised repair.

    This function never commits, merges or changes the trusted baseline.
    """

    relative_path = _normalize_relative(action.relative_path)

    if relative_path not in tuple(proposal.affected_files):
        return RepairResult(
            False,
            "TARGET_NOT_IN_PROPOSAL",
            relative_path,
        )

    protected = _protected(relative_path)

    approval_verified = False

    if protected:
        if approval is None:
            return RepairResult(
                False,
                "HUMAN_APPROVAL_REQUIRED",
                relative_path,
                protected=True,
            )

        try:
            approval_verified = verify_approval(
                proposal,
                approval,
                baseline=baseline,
            )
        except Exception:
            approval_verified = False

        if not approval_verified:
            return RepairResult(
                False,
                "INVALID_HUMAN_APPROVAL",
                relative_path,
                protected=True,
            )

    target = _resolve_target(root, relative_path)

    if target.exists():
        info = target.stat(follow_symlinks=False)

        if not stat.S_ISREG(info.st_mode):
            return RepairResult(
                False,
                "TARGET_NOT_REGULAR_FILE",
                relative_path,
                protected=protected,
                approval_verified=approval_verified,
            )

        before = target.read_bytes()
        before_hash = _digest(before)

    else:
        before_hash = None

    if before_hash != action.expected_sha256:
        return RepairResult(
            False,
            "PRECONDITION_HASH_MISMATCH",
            relative_path,
            before_sha256=before_hash,
            protected=protected,
            approval_verified=approval_verified,
        )

    # Protected repair authorization is single-use.
    # Consume it only after all non-mutating preconditions have passed,
    # immediately before the filesystem mutation.
    if protected:
        if approval_ledger is None:
            return RepairResult(
                False,
                "APPROVAL_LEDGER_REQUIRED",
                relative_path,
                before_sha256=before_hash,
                protected=True,
                approval_verified=approval_verified,
            )

        try:
            approval_ledger.consume(
                proposal,
                approval,
                baseline=baseline,
            )
        except Exception as exc:
            reason = str(exc) or type(exc).__name__
            return RepairResult(
                False,
                reason,
                relative_path,
                before_sha256=before_hash,
                protected=True,
                approval_verified=approval_verified,
            )

    _atomic_replace(target, action.replacement)

    after = target.read_bytes()
    after_hash = _digest(after)

    if after_hash != _digest(action.replacement):
        return RepairResult(
            False,
            "POST_WRITE_HASH_MISMATCH",
            relative_path,
            before_sha256=before_hash,
            after_sha256=after_hash,
            protected=protected,
            approval_verified=approval_verified,
        )

    return RepairResult(
        True,
        "REPAIR_APPLIED",
        relative_path,
        before_sha256=before_hash,
        after_sha256=after_hash,
        protected=protected,
        approval_verified=approval_verified,
    )


__all__ = [
    "RepairAction",
    "RepairResult",
    "RepairBackup",
    "capture_backup",
    "apply_repair",
    "rollback_repair",
    "AUTOMATIC_COMMIT",
    "AUTOMATIC_MERGE",
    "AUTOMATIC_BASELINE_UPDATE",
]


@dataclass(frozen=True)
class RepairBackup:
    relative_path: str
    existed: bool
    content: bytes | None
    sha256: str | None


def capture_backup(
    *,
    root: Path,
    relative_path: str,
) -> RepairBackup:
    """Capture exact pre-repair bytes for supervised rollback."""

    relative_path = _normalize_relative(relative_path)
    target = _resolve_target(root, relative_path)

    if not target.exists():
        return RepairBackup(
            relative_path=relative_path,
            existed=False,
            content=None,
            sha256=None,
        )

    info = target.stat(follow_symlinks=False)

    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError("BACKUP_TARGET_NOT_REGULAR_FILE")

    content = target.read_bytes()

    return RepairBackup(
        relative_path=relative_path,
        existed=True,
        content=content,
        sha256=_digest(content),
    )


def rollback_repair(
    *,
    root: Path,
    backup: RepairBackup,
    expected_current_sha256: str | None,
) -> RepairResult:
    """Restore the exact state captured immediately before a repair."""

    relative_path = _normalize_relative(backup.relative_path)
    target = _resolve_target(root, relative_path)
    protected = _protected(relative_path)

    if target.exists():
        info = target.stat(follow_symlinks=False)

        if not stat.S_ISREG(info.st_mode):
            return RepairResult(
                False,
                "ROLLBACK_TARGET_NOT_REGULAR_FILE",
                relative_path,
                protected=protected,
            )

        current = target.read_bytes()
        current_hash = _digest(current)
    else:
        current_hash = None

    if current_hash != expected_current_sha256:
        return RepairResult(
            False,
            "ROLLBACK_PRECONDITION_HASH_MISMATCH",
            relative_path,
            before_sha256=current_hash,
            protected=protected,
        )

    if backup.existed:
        if backup.content is None:
            return RepairResult(
                False,
                "INVALID_BACKUP",
                relative_path,
                protected=protected,
            )

        if _digest(backup.content) != backup.sha256:
            return RepairResult(
                False,
                "BACKUP_INTEGRITY_MISMATCH",
                relative_path,
                protected=protected,
            )

        _atomic_replace(target, backup.content)

        restored = target.read_bytes()
        restored_hash = _digest(restored)

        if restored_hash != backup.sha256:
            return RepairResult(
                False,
                "ROLLBACK_VERIFY_FAILED",
                relative_path,
                after_sha256=restored_hash,
                protected=protected,
            )

        return RepairResult(
            True,
            "ROLLBACK_APPLIED",
            relative_path,
            before_sha256=current_hash,
            after_sha256=restored_hash,
            protected=protected,
        )

    if target.exists():
        target.unlink()

        directory_fd = os.open(
            target.parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    if target.exists():
        return RepairResult(
            False,
            "ROLLBACK_DELETE_FAILED",
            relative_path,
            protected=protected,
        )

    return RepairResult(
        True,
        "ROLLBACK_APPLIED",
        relative_path,
        before_sha256=current_hash,
        after_sha256=None,
        protected=protected,
    )
