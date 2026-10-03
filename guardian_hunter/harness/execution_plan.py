"""Create bounded execution plans without executing providers."""

from __future__ import annotations

from dataclasses import dataclass

from guardian_hunter.harness.launcher import LaunchRequest
from guardian_hunter.harness.policy_bridge import (
    evaluate_with_containment,
)
from guardian_hunter.harness.providers import get_provider


@dataclass(frozen=True)
class ExecutionPlan:
    provider: str
    executable: str
    workspace: str
    capability: str
    target: str

    git_access: bool = False
    credential_access: bool = False
    master_access: bool = False
    trust_root_access: bool = False
    autonomous_merge: bool = False
    human_review_required: bool = True

    execution_allowed: bool = False


def build_plan(
    request: LaunchRequest,
) -> ExecutionPlan:

    decision = evaluate_with_containment(request)
    spec = get_provider(request.provider)

    return ExecutionPlan(
        provider=decision.provider,
        executable=spec.executable,
        workspace="/workspace",
        capability=decision.capability,
        target=decision.target,
    )
