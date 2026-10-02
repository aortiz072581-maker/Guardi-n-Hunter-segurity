"""Controlled adapter between an AI provider and Guardian workspace.

The adapter defines the boundary only. It does not contain credentials,
approve changes, merge code, or modify the protected repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


WORKSPACE = Path("/workspace")

FORBIDDEN_NAMES = frozenset(
    {
        ".git",
        ".ssh",
        ".gnupg",
        ".aws",
    }
)


@dataclass(frozen=True)
class AdapterPolicy:
    workspace: Path = WORKSPACE
    autonomous_execution: bool = False
    merge_allowed: bool = False
    protected_repository_access: bool = False


def validate_workspace(workspace: Path = WORKSPACE) -> Path:
    if workspace != WORKSPACE:
        raise ValueError("WORKSPACE_OUTSIDE_BOUNDARY")

    return workspace


def validate_relative_path(path: str) -> Path:
    if not path:
        raise ValueError("EMPTY_PATH")

    candidate = Path(path)

    if candidate.is_absolute():
        raise ValueError("ABSOLUTE_PATH_FORBIDDEN")

    if ".." in candidate.parts:
        raise ValueError("PATH_TRAVERSAL_FORBIDDEN")

    if any(part in FORBIDDEN_NAMES for part in candidate.parts):
        raise ValueError("FORBIDDEN_PATH")

    return candidate


def policy() -> AdapterPolicy:
    result = AdapterPolicy()

    if result.autonomous_execution:
        raise RuntimeError("AUTONOMOUS_EXECUTION_FORBIDDEN")

    if result.merge_allowed:
        raise RuntimeError("AGENT_MERGE_FORBIDDEN")

    if result.protected_repository_access:
        raise RuntimeError("PROTECTED_ACCESS_FORBIDDEN")

    return result
