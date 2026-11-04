"""Bridge between AI Harness and Guardian containment.

Both policy layers must independently approve a target.
Any disagreement fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass

from guardian_hunter.containment.ai_policy import path_allowed
from guardian_hunter.harness.launcher import (
    LaunchRequest,
    evaluate,
)


@dataclass(frozen=True)
class BridgeDecision:
    allowed: bool
    provider: str
    capability: str
    target: str
    reason: str


def evaluate_with_containment(
    request: LaunchRequest,
) -> BridgeDecision:

    harness = evaluate(request)

    if not harness.allowed:
        raise PermissionError("Harness rejected request")

    if not path_allowed(request.relative_path):
        raise PermissionError("Containment rejected path")

    return BridgeDecision(
        allowed=True,
        provider=harness.provider,
        capability=harness.capability,
        target=harness.target,
        reason="HARNESS_AND_CONTAINMENT_APPROVED",
    )
