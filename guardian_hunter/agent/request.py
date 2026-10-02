"""Create a bounded request for the detached Guardian agent."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRequest:
    objective: str
    autonomous_execution: bool = False
    merge_allowed: bool = False
    protected_changes_allowed: bool = False

    def validate(self) -> None:
        if not self.objective.strip():
            raise ValueError("EMPTY_OBJECTIVE")

        if self.autonomous_execution:
            raise ValueError("AUTONOMOUS_EXECUTION_FORBIDDEN")

        if self.merge_allowed:
            raise ValueError("AGENT_MERGE_FORBIDDEN")

        if self.protected_changes_allowed:
            raise ValueError("PROTECTED_CHANGES_FORBIDDEN")


def build_request(objective: str) -> AgentRequest:
    request = AgentRequest(objective=objective)
    request.validate()
    return request
