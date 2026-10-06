"""Read-only operational discovery for external AI providers.

This module does not send prompts, expose credentials, modify repositories,
or grant provider capabilities.  It only verifies provider versions through
the controlled Debian proot runtime.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import subprocess


PROOT_DISTRO = "proot-distro"
DISTRO = "debian"

PROVIDERS = {
    "codex": "/usr/local/bin/codex",
    "claude": "/usr/local/bin/claude",
    "aider": "/usr/local/bin/aider",
}


@dataclass(frozen=True)
class ProviderRuntime:
    provider: str
    installed: bool
    operational: bool
    runtime: str
    version: str | None
    reason: str
    authenticated: bool = False
    execution_allowed: bool = False


def _base_command() -> list[str]:
    executable = shutil.which(PROOT_DISTRO)
    if executable is None:
        raise FileNotFoundError("proot-distro unavailable")

    return [executable, "login", DISTRO, "--"]


def probe_provider(name: str) -> ProviderRuntime:
    path = PROVIDERS.get(name)

    if path is None:
        return ProviderRuntime(
            provider=name,
            installed=False,
            operational=False,
            runtime="debian-linux-arm64",
            version=None,
            reason="UNKNOWN_PROVIDER",
        )

    try:
        command = _base_command() + [path, "--version"]

        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
            env={
                "PATH": (
                    "/data/data/com.termux/files/usr/bin:"
                    "/system/bin:/system/xbin"
                )
            },
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ProviderRuntime(
            provider=name,
            installed=False,
            operational=False,
            runtime="debian-linux-arm64",
            version=None,
            reason="PROBE_FAILED",
        )

    output = (completed.stdout or "").strip()

    if completed.returncode != 0 or not output:
        return ProviderRuntime(
            provider=name,
            installed=False,
            operational=False,
            runtime="debian-linux-arm64",
            version=None,
            reason="VERSION_CHECK_FAILED",
        )

    return ProviderRuntime(
        provider=name,
        installed=True,
        operational=True,
        runtime="debian-linux-arm64",
        version=output.splitlines()[0][:200],
        reason="VERSION_CHECK_PASSED",
    )


def discover_provider_runtimes() -> dict[str, dict[str, object]]:
    return {
        name: asdict(probe_provider(name))
        for name in PROVIDERS
    }
