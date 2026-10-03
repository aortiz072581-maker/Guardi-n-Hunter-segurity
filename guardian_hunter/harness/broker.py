"""Guardian-controlled external AI execution broker.

The broker is the only component intended to launch an AI provider.
This phase supports validation and dry-run only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from guardian_hunter.harness.execution_plan import build_plan
from guardian_hunter.harness.launcher import LaunchRequest


WORKSPACE = Path("/workspace")
TIMEOUT_SECONDS = 300

CREDENTIAL_NAMES = frozenset({
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT_ID",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "SSH_AUTH_SOCK",
})


@dataclass(frozen=True)
class BrokerResult:
    provider: str
    target: str
    workspace: str
    dry_run: bool
    executed: bool
    credentials_present: bool
    git_available: bool
    timeout_seconds: int
    reason: str


def sanitized_environment() -> dict[str, str]:
    env = {
        "HOME": "/tmp/guardian-agent-home",
        "USER": "guardian-agent",
        "LOGNAME": "guardian-agent",
        "PATH": (
            "/opt/guardian-agents/bin:"
            "/opt/guardian-agents/node22/bin:"
            "/usr/local/bin:/usr/bin:/bin"
        ),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "GUARDIAN_WORKSPACE": "/workspace",
        "GUARDIAN_AUTONOMOUS_MERGE": "0",
        "GUARDIAN_HUMAN_REVIEW_REQUIRED": "1",
    }

    for name in CREDENTIAL_NAMES:
        env.pop(name, None)

    return env


def environment_is_sanitized(
    env: dict[str, str],
) -> bool:
    return not any(
        name in env
        for name in CREDENTIAL_NAMES
    )


def prepare(
    request: LaunchRequest,
    *,
    dry_run: bool = True,
) -> BrokerResult:

    if not dry_run:
        raise PermissionError(
            "Real provider execution not enabled"
        )

    plan = build_plan(request)

    if plan.execution_allowed:
        raise PermissionError(
            "Unexpected execution authority"
        )

    env = sanitized_environment()

    if not environment_is_sanitized(env):
        raise PermissionError(
            "Credential environment not sanitized"
        )

    if plan.workspace != str(WORKSPACE):
        raise PermissionError(
            "Unexpected workspace"
        )

    return BrokerResult(
        provider=plan.provider,
        target=plan.target,
        workspace=plan.workspace,
        dry_run=True,
        executed=False,
        credentials_present=False,
        git_available=False,
        timeout_seconds=TIMEOUT_SECONDS,
        reason="VALIDATED_DRY_RUN_ONLY",
    )


def host_credentials_visible() -> tuple[str, ...]:
    return tuple(
        sorted(
            name
            for name in CREDENTIAL_NAMES
            if os.environ.get(name)
        )
    )
