"""Controlled provider launcher.

This module validates requests. It does not grant providers
authority over Guardian Hunter.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from guardian_hunter.harness.capabilities import require_capability
from guardian_hunter.harness.providers import (
    get_provider,
    validate_provider,
)


WORKSPACE = PurePosixPath("/workspace")

DENIED_PARTS = frozenset(
    {
        ".git",
        ".guardian",
    }
)

DENIED_PREFIXES = (
    PurePosixPath("guardian_hunter/gate"),
    PurePosixPath("guardian_hunter/security"),
    PurePosixPath("guardian_hunter/governance"),
    PurePosixPath("guardian_hunter/containment"),
    PurePosixPath("guardian_hunter/harness"),
)


@dataclass(frozen=True)
class LaunchRequest:
    provider: str
    capability: str
    relative_path: str


@dataclass(frozen=True)
class LaunchDecision:
    allowed: bool
    provider: str
    capability: str
    target: str
    reason: str


def validate_path(relative_path: str) -> PurePosixPath:
    raw = PurePosixPath(relative_path)

    if raw.is_absolute():
        raise PermissionError("Absolute path denied")

    if not raw.parts:
        raise PermissionError("Empty path denied")

    if ".." in raw.parts:
        raise PermissionError("Path escape denied")

    if any(part in DENIED_PARTS for part in raw.parts):
        raise PermissionError("Protected metadata denied")

    for prefix in DENIED_PREFIXES:
        try:
            raw.relative_to(prefix)
        except ValueError:
            continue
        raise PermissionError(f"Protected path denied: {prefix}")

    return raw


def evaluate(request: LaunchRequest) -> LaunchDecision:
    spec = get_provider(request.provider)
    validate_provider(spec)

    capability = require_capability(request.capability)

    path = validate_path(request.relative_path)

    target = WORKSPACE / path

    return LaunchDecision(
        allowed=True,
        provider=spec.name.value,
        capability=capability.value,
        target=str(target),
        reason="BOUNDED_REQUEST_ACCEPTED",
    )
