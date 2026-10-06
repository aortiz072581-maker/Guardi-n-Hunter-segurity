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


def _open_parent_dirfd(
    root: Path,
    relative_path: str,
) -> tuple[int, str]:
    """Open the target parent anchored to root without following symlinks."""

    relative_path = _normalize_relative(relative_path)
    parts = relative_path.split("/")
    leaf = parts[-1]

    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )

    root_fd = os.open(root, flags)
    current_fd = root_fd

    try:
        for part in parts[:-1]:
            next_fd = os.open(
                part,
                flags,
                dir_fd=current_fd,
            )

            if current_fd != root_fd:
                os.close(current_fd)

            current_fd = next_fd

        if current_fd == root_fd:
            root_fd = -1

        return current_fd, leaf

    except Exception:
        if current_fd != root_fd:
            os.close(current_fd)
        raise

    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _read_regular_at(
    parent_fd: int,
    leaf: str,
) -> bytes:
    """Read one regular file without following the final symlink."""

    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )

    fd = os.open(
        leaf,
        flags,
        dir_fd=parent_fd,
    )

    try:
        info = os.fstat(fd)

        if not stat.S_ISREG(info.st_mode):
            raise RuntimeError("REPAIR_TARGET_NOT_REGULAR_FILE")

        chunks = []

        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)

        return b"".join(chunks)

    finally:
        os.close(fd)


def _atomic_replace_at(
    parent_fd: int,
    leaf: str,
    content: bytes,
) -> None:
    """Atomically replace a leaf anchored to an already verified directory."""

    if (
        not leaf
        or "/" in leaf
        or leaf in (".", "..")
        or "\x00" in leaf
    ):
        raise ValueError("INVALID_REPAIR_LEAF")

    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )

    temporary = (
        ".guardian-repair-"
        + os.urandom(16).hex()
    )

    fd = None

    try:
        fd = os.open(
            temporary,
            flags,
            0o600,
            dir_fd=parent_fd,
        )

        view = memoryview(content)

        while view:
            written = os.write(fd, view)

            if written <= 0:
                raise OSError("REPAIR_SHORT_WRITE")

            view = view[written:]

        os.fsync(fd)
        os.close(fd)
        fd = None

        os.rename(
            temporary,
            leaf,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )

        os.fsync(parent_fd)

    finally:
        if fd is not None:
            os.close(fd)

        try:
            os.unlink(
                temporary,
                dir_fd=parent_fd,
            )
        except FileNotFoundError:
            pass


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

    Filesystem access is anchored to an opened root directory. Intermediate
    and final symlinks are not followed. This function never commits, merges
    or changes the trusted baseline.
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

    try:
        parent_fd, leaf = _open_parent_dirfd(root, relative_path)
    except (OSError, RuntimeError, ValueError):
        return RepairResult(
            False,
            "TARGET_PATH_UNSAFE",
            relative_path,
            protected=protected,
            approval_verified=approval_verified,
        )

    try:
        try:
            before = _read_regular_at(parent_fd, leaf)
            before_hash = _digest(before)
        except FileNotFoundError:
            before = None
            before_hash = None
        except (OSError, RuntimeError):
            return RepairResult(
                False,
                "TARGET_NOT_REGULAR_FILE",
                relative_path,
                protected=protected,
                approval_verified=approval_verified,
            )

        if before_hash != action.expected_sha256:
            return RepairResult(
                False,
                "PRECONDITION_HASH_MISMATCH",
                relative_path,
                before_sha256=before_hash,
                protected=protected,
                approval_verified=approval_verified,
            )

        # Protected authorization is single-use and is consumed only after
        # every non-mutating filesystem precondition has succeeded.
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

        try:
            _atomic_replace_at(
                parent_fd,
                leaf,
                action.replacement,
            )
            after = _read_regular_at(parent_fd, leaf)
        except (OSError, RuntimeError):
            return RepairResult(
                False,
                "REPAIR_WRITE_FAILED",
                relative_path,
                before_sha256=before_hash,
                protected=protected,
                approval_verified=approval_verified,
            )

        after_hash = _digest(after)
        expected_after = _digest(action.replacement)

        if after_hash != expected_after:
            # The write occurred but verification failed. Restore the exact
            # pre-write state before returning control.
            backup = RepairBackup(
                relative_path=relative_path,
                existed=before is not None,
                content=before,
                sha256=before_hash,
            )

            try:
                rollback = rollback_repair(
                    root=root,
                    backup=backup,
                    expected_current_sha256=after_hash,
                )
            except Exception:
                return RepairResult(
                    False,
                    "POST_WRITE_HASH_MISMATCH_ROLLBACK_FAILED",
                    relative_path,
                    before_sha256=before_hash,
                    after_sha256=after_hash,
                    protected=protected,
                    approval_verified=approval_verified,
                )

            if not rollback.applied:
                return RepairResult(
                    False,
                    "POST_WRITE_HASH_MISMATCH_ROLLBACK_FAILED",
                    relative_path,
                    before_sha256=before_hash,
                    after_sha256=rollback.after_sha256,
                    protected=protected,
                    approval_verified=approval_verified,
                )

            return RepairResult(
                False,
                "POST_WRITE_HASH_MISMATCH_ROLLED_BACK",
                relative_path,
                before_sha256=before_hash,
                after_sha256=rollback.after_sha256,
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

    finally:
        os.close(parent_fd)


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
    """Capture exact pre-repair bytes without following symlinks."""

    relative_path = _normalize_relative(relative_path)
    parent_fd, leaf = _open_parent_dirfd(root, relative_path)

    try:
        try:
            content = _read_regular_at(parent_fd, leaf)
        except FileNotFoundError:
            return RepairBackup(
                relative_path=relative_path,
                existed=False,
                content=None,
                sha256=None,
            )
        except (OSError, RuntimeError) as exc:
            raise RuntimeError(
                "BACKUP_TARGET_NOT_REGULAR_FILE"
            ) from exc

        return RepairBackup(
            relative_path=relative_path,
            existed=True,
            content=content,
            sha256=_digest(content),
        )

    finally:
        os.close(parent_fd)


def rollback_repair(
    *,
    root: Path,
    backup: RepairBackup,
    expected_current_sha256: str | None,
) -> RepairResult:
    """Restore the exact state captured immediately before a repair."""

    relative_path = _normalize_relative(backup.relative_path)
    protected = _protected(relative_path)

    try:
        parent_fd, leaf = _open_parent_dirfd(root, relative_path)
    except (OSError, RuntimeError, ValueError):
        return RepairResult(
            False,
            "ROLLBACK_PATH_UNSAFE",
            relative_path,
            protected=protected,
        )

    try:
        try:
            current = _read_regular_at(parent_fd, leaf)
            current_hash = _digest(current)
            current_exists = True
        except FileNotFoundError:
            current = None
            current_hash = None
            current_exists = False
        except (OSError, RuntimeError):
            return RepairResult(
                False,
                "ROLLBACK_TARGET_NOT_REGULAR_FILE",
                relative_path,
                protected=protected,
            )

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

            try:
                _atomic_replace_at(
                    parent_fd,
                    leaf,
                    backup.content,
                )
                restored = _read_regular_at(parent_fd, leaf)
            except (OSError, RuntimeError):
                return RepairResult(
                    False,
                    "ROLLBACK_WRITE_FAILED",
                    relative_path,
                    before_sha256=current_hash,
                    protected=protected,
                )

            restored_hash = _digest(restored)

            if restored_hash != backup.sha256:
                return RepairResult(
                    False,
                    "ROLLBACK_VERIFY_FAILED",
                    relative_path,
                    before_sha256=current_hash,
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

        if current_exists:
            try:
                os.unlink(
                    leaf,
                    dir_fd=parent_fd,
                )
                os.fsync(parent_fd)
            except OSError:
                return RepairResult(
                    False,
                    "ROLLBACK_DELETE_FAILED",
                    relative_path,
                    before_sha256=current_hash,
                    protected=protected,
                )

        # Verify through the same anchored descriptor. A replacement symlink
        # is also considered failure rather than being followed.
        try:
            _read_regular_at(parent_fd, leaf)
        except FileNotFoundError:
            pass
        except (OSError, RuntimeError):
            return RepairResult(
                False,
                "ROLLBACK_DELETE_VERIFY_FAILED",
                relative_path,
                before_sha256=current_hash,
                protected=protected,
            )
        else:
            return RepairResult(
                False,
                "ROLLBACK_DELETE_FAILED",
                relative_path,
                before_sha256=current_hash,
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

    finally:
        os.close(parent_fd)


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
