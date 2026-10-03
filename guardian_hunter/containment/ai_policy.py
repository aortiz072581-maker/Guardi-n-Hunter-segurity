"""Fail-closed policy shared by every external AI provider."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class AIContainmentPolicy:
    workspace_root: str = "/workspace"

    auto_merge: bool = False
    master_access: bool = False
    protected_git_access: bool = False
    baseline_modification: bool = False
    signing_key_access: bool = False
    gate_modification: bool = False
    self_permission_change: bool = False

    human_review_required: bool = True


POLICY = AIContainmentPolicy()


DENIED_PARTS = frozenset({
    ".git",
    ".guardian",
})

DENIED_PREFIXES = (
    "guardian_hunter/gate/",
    "guardian_hunter/security/",
    "guardian_hunter/governance/",
    "guardian_hunter/containment/",
    "guardian_hunter/harness/",
)

SENSITIVE_NAMES = frozenset({
    "trusted-baseline",
    "id_rsa",
    "id_ed25519",
    "authorized_keys",
})


def validate_policy() -> bool:
    return (
        POLICY.auto_merge is False
        and POLICY.master_access is False
        and POLICY.protected_git_access is False
        and POLICY.baseline_modification is False
        and POLICY.signing_key_access is False
        and POLICY.gate_modification is False
        and POLICY.self_permission_change is False
        and POLICY.human_review_required is True
    )


def path_allowed(relative_path: str) -> bool:
    if not relative_path or "\x00" in relative_path:
        return False

    raw = relative_path.replace("\\", "/")
    path = PurePosixPath(raw)

    if path.is_absolute():
        return False

    if ".." in path.parts:
        return False

    if any(part in DENIED_PARTS for part in path.parts):
        return False

    if any(part in SENSITIVE_NAMES for part in path.parts):
        return False

    normalized = path.as_posix().lstrip("./")

    if any(normalized.startswith(prefix) for prefix in DENIED_PREFIXES):
        return False

    return True
