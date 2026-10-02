"""Fail-closed command boundary for external AI providers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
import shlex

from guardian_hunter.containment.ai_policy import path_allowed


@dataclass(frozen=True)
class ProviderDecision:
    allowed: bool
    reason: str


ALLOWED_EXECUTABLES = frozenset({
    "python",
    "python3",
    "pytest",
})

SHELL_META = re.compile(r"[;&|`$<>]")


def _safe_argument(value: str) -> bool:
    if "\x00" in value:
        return False

    if SHELL_META.search(value):
        return False

    # Options are allowed, but never interpreted as paths here.
    if value.startswith("-"):
        return True

    # Simple non-path values are acceptable.
    if "/" not in value and "\\" not in value:
        return True

    normalized = value.replace("\\", "/")

    if PurePosixPath(normalized).is_absolute():
        return False

    return path_allowed(normalized)


def validate_command(command: str) -> ProviderDecision:
    if not command or "\x00" in command:
        return ProviderDecision(False, "EMPTY_OR_INVALID")

    if SHELL_META.search(command):
        return ProviderDecision(False, "SHELL_CONTROL_DENIED")

    try:
        parts = shlex.split(command)
    except ValueError:
        return ProviderDecision(False, "PARSE_FAILED")

    if not parts:
        return ProviderDecision(False, "EMPTY_COMMAND")

    executable = PurePosixPath(parts[0]).name

    if executable not in ALLOWED_EXECUTABLES:
        return ProviderDecision(False, "EXECUTABLE_DENIED")

    for argument in parts[1:]:
        if not _safe_argument(argument):
            return ProviderDecision(False, "ARGUMENT_DENIED")

    return ProviderDecision(True, "ALLOWED")
