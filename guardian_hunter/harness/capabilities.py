"""Capabilities exposed to external AI providers."""

from __future__ import annotations

from enum import Enum


class Capability(str, Enum):
    READ_WORKSPACE = "read_workspace"
    PROPOSE_EDIT = "propose_edit"
    RUN_APPROVED_TEST = "run_approved_test"


ALLOWED_CAPABILITIES = frozenset({
    Capability.READ_WORKSPACE,
    Capability.PROPOSE_EDIT,
    Capability.RUN_APPROVED_TEST,
})


DENIED_CAPABILITIES = frozenset({
    "git",
    "shell",
    "master_access",
    "trust_root",
    "baseline_write",
    "signing_key",
    "gate_write",
    "containment_write",
    "credential_dump",
    "permission_change",
    "auto_merge",
})


def require_capability(name: str) -> Capability:
    try:
        capability = Capability(name)
    except ValueError as exc:
        raise PermissionError(
            f"Capability denied: {name}"
        ) from exc

    if capability not in ALLOWED_CAPABILITIES:
        raise PermissionError(
            f"Capability denied: {name}"
        )

    return capability
