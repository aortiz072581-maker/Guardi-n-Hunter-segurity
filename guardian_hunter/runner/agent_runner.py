"""Controlled runner for the detached Guardian Agent workspace."""

from __future__ import annotations

import os
import subprocess
import stat
import sys
import tempfile
from pathlib import Path


TIMEOUT_SECONDS = 300

ALLOWED_EXECUTABLES = frozenset({
    "python",
    "python3",
})

FORBIDDEN_ARGUMENT_TOKENS = (
    ";",
    "&&",
    "||",
    "|",
    "`",
    "$(",
    "\n",
    "\r",
    "\x00",
)

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
        "PATH": str(Path(sys.executable).resolve().parent),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", ""),
        "TERM": os.environ.get("TERM", "xterm-256color"),
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


def validate_command(command: list[str]) -> None:
    """Reject unauthorized candidate commands before process creation."""

    if not command:
        raise RuntimeError("COMMAND_REQUIRED")

    if not all(isinstance(item, str) and item for item in command):
        raise RuntimeError("INVALID_COMMAND_ARGUMENT")

    executable = command[0]

    if (
        executable not in ALLOWED_EXECUTABLES
        or Path(executable).name != executable
        or "/" in executable
        or "\\" in executable
    ):
        raise RuntimeError("EXECUTABLE_NOT_ALLOWED")

    arguments = command[1:]

    if not arguments:
        raise RuntimeError("SCRIPT_REQUIRED")

    # Python is an interpreter, so executable allowlisting alone is
    # insufficient. Only a relative .py script in the detached workspace
    # may be selected. Interpreter switches such as -c and -m fail closed.
    script = arguments[0]

    if script.startswith("-"):
        raise RuntimeError("UNSAFE_COMMAND_ARGUMENT")

    script_path = Path(script)

    if (
        script_path.is_absolute()
        or ".." in script_path.parts
        or script_path.suffix != ".py"
        or "\x00" in script
    ):
        raise RuntimeError("UNSAFE_COMMAND_ARGUMENT")

    for argument in arguments:
        if any(
            token in argument
            for token in FORBIDDEN_ARGUMENT_TOKENS
        ):
            raise RuntimeError("UNSAFE_COMMAND_ARGUMENT")


def validate_script(workspace: Path, script: str) -> Path:
    """Require a real regular script physically confined to workspace."""

    workspace = workspace.resolve()
    relative = Path(script)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix != ".py"
        or "\\x00" in script
    ):
        raise RuntimeError("UNSAFE_COMMAND_ARGUMENT")

    candidate = workspace / relative

    # Reject symlinks in every path component before resolution.
    current = workspace

    for part in relative.parts:
        current = current / part

        if current.is_symlink():
            raise RuntimeError("SCRIPT_SYMLINK_FORBIDDEN")

    try:
        resolved = candidate.resolve(strict=True)
    except (FileNotFoundError, OSError):
        raise RuntimeError("SCRIPT_NOT_REGULAR_FILE")

    try:
        resolved.relative_to(workspace)
    except ValueError:
        raise RuntimeError("SCRIPT_OUTSIDE_WORKSPACE")

    if not resolved.is_file():
        raise RuntimeError("SCRIPT_NOT_REGULAR_FILE")

    return resolved


def run_candidate(command: list[str]) -> int:
    protected = Path.cwd().resolve()
    workspace = (protected.parent / "guardian-agent").resolve()

    validate_workspace(workspace)
    validate_command(command)

    validated_script = validate_script(
        workspace,
        command[1],
    )

    try:
        validated_stat = validated_script.stat(
            follow_symlinks=False
        )
    except OSError as exc:
        raise RuntimeError(
            "SCRIPT_IDENTITY_UNAVAILABLE"
        ) from exc

    if not stat.S_ISREG(validated_stat.st_mode):
        raise RuntimeError(
            "SCRIPT_NOT_REGULAR_FILE"
        )

    env = sanitized_environment(workspace)

    flags = (
        os.O_RDONLY
        | os.O_NOFOLLOW
        | os.O_CLOEXEC
    )

    try:
        script_fd = os.open(
            validated_script,
            flags,
        )

    except OSError as exc:
        raise RuntimeError(
            "SCRIPT_SECURE_OPEN_FAILED"
        ) from exc

    try:
        opened = os.fstat(script_fd)

        if not stat.S_ISREG(opened.st_mode):
            raise RuntimeError(
                "SCRIPT_NOT_REGULAR_FILE"
            )

        if (
            opened.st_dev != validated_stat.st_dev
            or opened.st_ino != validated_stat.st_ino
        ):
            raise RuntimeError(
                "SCRIPT_IDENTITY_CHANGED"
            )

        trusted_python = str(
            Path(sys.executable).resolve()
        )

        # Freeze the exact candidate bytes before execution.
        # The agent workspace remains untrusted and mutable, so Python
        # must never execute the workspace file directly.
        snapshot_dir = Path(
            tempfile.mkdtemp(
                prefix="guardian-runner-",
            )
        )

        try:
            os.chmod(snapshot_dir, 0o700)

            snapshot = snapshot_dir / "candidate.py"

            with os.fdopen(
                os.dup(script_fd),
                "rb",
                closefd=True,
            ) as source:
                candidate_bytes = source.read()

            snapshot_fd = os.open(
                snapshot,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | os.O_NOFOLLOW,
                0o400,
            )

            try:
                view = memoryview(candidate_bytes)

                while view:
                    written = os.write(snapshot_fd, view)

                    if written <= 0:
                        raise RuntimeError(
                            "SCRIPT_SNAPSHOT_WRITE_FAILED"
                        )

                    view = view[written:]

                os.fsync(snapshot_fd)
            finally:
                os.close(snapshot_fd)

            # -I blocks PYTHONPATH, user-site and startup injection.
            # We add the detached workspace only AFTER interpreter
            # initialization so legitimate sibling imports still work.
            launcher = (
                "import runpy,sys;"
                f"sys.path.insert(0,{str(workspace)!r});"
                f"sys.argv={[str(snapshot), *command[2:]]!r};"
                f"runpy.run_path({str(snapshot)!r},run_name='__main__')"
            )

            resolved_command = [
                trusted_python,
                "-I",
                "-c",
                launcher,
            ]

            try:
                result = subprocess.run(
                    resolved_command,
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

        finally:
            try:
                snapshot.unlink(missing_ok=True)
            finally:
                snapshot_dir.rmdir()

    finally:
        os.close(script_fd)


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
