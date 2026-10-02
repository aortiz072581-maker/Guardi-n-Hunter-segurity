"""Security contract for external AI coding agents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentContract:
    workspace_only: bool = True
    git_access: bool = False
    credential_access: bool = False
    protected_repository_access: bool = False
    autonomous_execution: bool = False
    merge_allowed: bool = False
    human_review_required: bool = True


def contract() -> AgentContract:
    return AgentContract()


def validate_contract(value: AgentContract) -> bool:
    return (
        value.workspace_only is True
        and value.git_access is False
        and value.credential_access is False
        and value.protected_repository_access is False
        and value.autonomous_execution is False
        and value.merge_allowed is False
        and value.human_review_required is True
    )
