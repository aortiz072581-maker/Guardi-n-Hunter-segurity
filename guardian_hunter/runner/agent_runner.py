"""Controlled runner for the detached Guardian Agent workspace."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


TIMEOUT_SECONDS = 300

BLOCKED_ENV_PREFIXES = (
    "GITHUB_",
    "GH_",
    "AWS_",
    "AZURE_",
    "GOOGLE_",
    "OPENAI_",
    "ANTHROPIC_",
)

BLOCKED_ENV_NAMES = {
    "SSH_AUTH_SOCK",
    "GIT_ASKPASS",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
}


def sanitized_environment(workspace: Path) -> dict[str, str]:
    allowed = {
        "HOME": str(workspace),
        "PATH": os.environ.get("PATH", ""),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", ""),
        "TERM": os.environ.get("TERM", "xterm-256color"),
        "PYTHONPATH": str(workspace),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }

    for name in tuple(allowed):
        if not allowed[name]:
            allowed.pop(name)

    for name in BLOCKED_ENV_NAMES:
        allowed.pop(name, None)

    for name in tuple(allowed):
        if name.startswith(BLOCKED_ENV_PREFIXES):
            allowed.pop(name, None)

    return allowed


def validate_workspace(workspace: Path) -> None:
    if not workspace.is_dir():
        raise RuntimeError("WORKSPACE_MISSING")

    if (workspace / ".git").exists():
        raise RuntimeError("WORKSPACE_GIT_FORBIDDEN")


def run_candidate(command: list[str]) -> int:
    protected = Path.cwd().resolve()
    workspace = (protected.parent / "guardian-agent").resolve()

    validate_workspace(workspace)

    if not command:
        raise RuntimeError("COMMAND_REQUIRED")

    env = sanitized_environment(workspace)

    try:
        result = subprocess.run(
            command,
            cwd=workspace,
            env=env,
            stdin=subprocess.DEVNULL,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("RUNNER: TIMEOUT")
        return 124

    return result.returncode


def main() -> int:
    # Intentionally no arbitrary CLI command interface yet.
    print("GUARDIAN CONTROLLED RUNNER")
    print("WORKSPACE: guardian-agent")
    print("GIT ACCESS: NOT PROVIDED")
    print("CREDENTIAL ENVIRONMENT: SANITIZED")
    print("TIMEOUT:", TIMEOUT_SECONDS)
    print("AUTONOMOUS EXECUTION: NOT ENABLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
