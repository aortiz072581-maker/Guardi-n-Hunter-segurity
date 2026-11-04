"""Fail-closed registry for external AI providers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Provider(str, Enum):
    CLAUDE = "claude"
    AIDER = "aider"
    CODEX = "codex"


@dataclass(frozen=True)
class ProviderSpec:
    name: Provider
    executable: str
    workspace_only: bool = True
    git_access: bool = False
    master_access: bool = False
    trust_root_access: bool = False
    credential_passthrough: bool = False
    autonomous_merge: bool = False
    gate_modification: bool = False
    human_review_required: bool = True


PROVIDERS = {
    Provider.CLAUDE: ProviderSpec(
        Provider.CLAUDE,
        "/opt/guardian-agents/bin/claude",
    ),
    Provider.AIDER: ProviderSpec(
        Provider.AIDER,
        "/opt/guardian-agents/bin/aider",
    ),
    Provider.CODEX: ProviderSpec(
        Provider.CODEX,
        "/opt/guardian-agents/bin/codex",
    ),
}


def get_provider(name: str) -> ProviderSpec:
    try:
        provider = Provider(name)
    except ValueError as exc:
        raise PermissionError(f"Unknown provider denied: {name}") from exc

    return PROVIDERS[provider]


def validate_provider(spec: ProviderSpec) -> None:
    required = {
        "workspace_only": True,
        "git_access": False,
        "master_access": False,
        "trust_root_access": False,
        "credential_passthrough": False,
        "autonomous_merge": False,
        "gate_modification": False,
        "human_review_required": True,
    }

    for field, expected in required.items():
        actual = getattr(spec, field)

        if actual != expected:
            raise PermissionError(f"Provider policy violation: {field}={actual!r}")
