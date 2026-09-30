"""Phases 139→141 — defensive Node.js runtime bridge.

The bridge is intentionally fail-closed:
- no real execution
- no subprocess invocation
- no shell execution
- no file mutation
- human review remains mandatory
"""

from dataclasses import dataclass


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass(frozen=True)
class NodeRuntimeState:
    available: bool
    version: str | None
    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool
    execution_allowed: bool


def build_runtime_state(
    *,
    node_available: bool = False,
    node_version: str | None = None,
) -> NodeRuntimeState:
    """Build a fail-closed Node.js runtime state.

    Runtime availability never grants permission to execute.
    """

    return NodeRuntimeState(
        available=bool(node_available),
        version=node_version,
        read_only=READ_ONLY,
        dry_run=DRY_RUN,
        real_execution_blocked=REAL_EXECUTION_BLOCKED,
        human_review_required=HUMAN_REVIEW_REQUIRED,
        response_locked=RESPONSE_LOCKED,
        execution_allowed=False,
    )


def runtime_contract() -> dict[str, object]:
    """Return the immutable defensive runtime contract."""

    return {
        "READ_ONLY": READ_ONLY,
        "DRY_RUN": DRY_RUN,
        "REAL_EXECUTION_BLOCKED": REAL_EXECUTION_BLOCKED,
        "HUMAN_REVIEW_REQUIRED": HUMAN_REVIEW_REQUIRED,
        "RESPONSE_LOCKED": RESPONSE_LOCKED,
        "EXECUTION_ALLOWED": False,
    }
