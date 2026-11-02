"""Guardian Hunter — controlled PRoot candidate runner."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


TIMEOUT = 300

SAFE_ENV = {
    "HOME": "/root",
    "PATH": (
        "/usr/local/sbin:/usr/local/bin:"
        "/usr/sbin:/usr/bin:/sbin:/bin"
    ),
    "LANG": "C.UTF-8",
}


def main() -> int:
    print("REASON: TRUSTED_EXECUTION_BROKER_NOT_CONFIGURED")
    return 1
    home = Path.home()
    workspace = home / "guardian-agent"

    if not workspace.is_dir():
        print("RESULT: FAIL")
        print("REASON: WORKSPACE_MISSING")
        return 1

    if (workspace / ".git").exists():
        print("RESULT: FAIL")
        print("REASON: WORKSPACE_GIT_FORBIDDEN")
        return 1

    protected = home / "guardian-hunter"

    try:
        if workspace.resolve() == protected.resolve():
            print("RESULT: FAIL")
            print("REASON: PROTECTED_WORKSPACE_FORBIDDEN")
            return 1
    except OSError:
        print("RESULT: FAIL")
        print("REASON: WORKSPACE_RESOLUTION_FAILED")
        return 1

    if (workspace / ".git").exists():
        print("RESULT: FAIL")
        print("REASON: GIT_METADATA_PRESENT")
        return 1

    command = [
        "proot-distro",
        "login",
        "debian",
        "--bind",
        f"{workspace}:/workspace",
        "--",
        "/usr/bin/env",
        "-i",
    ]

    for name, value in SAFE_ENV.items():
        command.append(f"{name}={value}")

    command.extend(
        [
            "/bin/sh",
            "-c",
            (
                "set -eu; "
                "cd /workspace; "
                "test ! -e .git; "
                'echo "CONTROLLED ENVIRONMENT: ACTIVE"; '
                'echo "WORKSPACE: /workspace"; '
                'echo "GIT ACCESS: NOT PROVIDED"; '
                'echo "CREDENTIAL ENVIRONMENT: SANITIZED"'
            ),
        ]
    )

    try:
        result = subprocess.run(
            command,
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
            },
            timeout=TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("RESULT: FAIL")
        print("REASON: TIMEOUT")
        return 1
    except Exception as exc:
        print("RESULT: FAIL")
        print("REASON:", type(exc).__name__)
        return 1

    if result.returncode != 0:
        print("RESULT: FAIL")
        print("REASON: PROOT_EXECUTION_FAILED")
        return 1

    print("TIMEOUT:", TIMEOUT)
    print("AUTONOMOUS EXECUTION: NOT ENABLED")
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
