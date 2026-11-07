"""Adversarial tests for the detached Guardian Agent runner."""

from pathlib import Path

import pytest

from guardian_hunter.runner import agent_runner


def test_empty_command_is_rejected(monkeypatch, tmp_path):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    monkeypatch.chdir(protected)

    with pytest.raises(RuntimeError, match="COMMAND_REQUIRED"):
        agent_runner.run_candidate([])


def test_arbitrary_executable_is_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    monkeypatch.chdir(protected)

    called = False

    def forbidden_run(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError(
            "subprocess must not run for an unauthorized executable"
        )

    monkeypatch.setattr(agent_runner.subprocess, "run", forbidden_run)

    with pytest.raises(RuntimeError, match="EXECUTABLE_NOT_ALLOWED"):
        agent_runner.run_candidate(
            ["sh", "-c", "echo unauthorized"]
        )

    assert called is False


def test_git_is_rejected_before_subprocess(monkeypatch, tmp_path):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError("git must never reach subprocess")

    monkeypatch.setattr(agent_runner.subprocess, "run", forbidden_run)

    with pytest.raises(RuntimeError, match="EXECUTABLE_NOT_ALLOWED"):
        agent_runner.run_candidate(["git", "status"])


def test_path_like_executable_is_rejected(monkeypatch, tmp_path):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "path-based executable must never reach subprocess"
        )

    monkeypatch.setattr(agent_runner.subprocess, "run", forbidden_run)

    with pytest.raises(RuntimeError, match="EXECUTABLE_NOT_ALLOWED"):
        agent_runner.run_candidate(
            ["/bin/sh", "-c", "echo unauthorized"]
        )


def test_workspace_with_git_metadata_is_rejected(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()
    (workspace / ".git").mkdir()

    monkeypatch.chdir(protected)

    with pytest.raises(RuntimeError, match="WORKSPACE_GIT_FORBIDDEN"):
        agent_runner.run_candidate(["python", "--version"])


def test_sanitized_environment_does_not_pass_credentials(
    monkeypatch,
    tmp_path,
):
    workspace = tmp_path / "guardian-agent"
    workspace.mkdir()

    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "secret")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/agent.sock")

    env = agent_runner.sanitized_environment(workspace)

    assert "OPENAI_API_KEY" not in env
    assert "ANTHROPIC_API_KEY" not in env
    assert "GITHUB_TOKEN" not in env
    assert "AWS_SECRET_ACCESS_KEY" not in env
    assert "SSH_AUTH_SOCK" not in env

    assert env["HOME"] == str(workspace)
    assert "PYTHONPATH" not in env


def test_runner_has_finite_timeout():
    assert isinstance(agent_runner.TIMEOUT_SECONDS, int)
    assert 1 <= agent_runner.TIMEOUT_SECONDS <= 300


@pytest.mark.parametrize(
    "command",
    [
        ["python", "-c", "print('candidate code')"],
        ["python3", "-c", "print('candidate code')"],
        ["python", "-m", "subprocess"],
        ["python3", "-m", "os"],
    ],
)
def test_python_code_execution_switches_are_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
    command,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    monkeypatch.chdir(protected)

    called = False

    def forbidden_run(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError(
            "Python execution switch reached subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match="UNSAFE_COMMAND_ARGUMENT",
    ):
        agent_runner.run_candidate(command)

    assert called is False


@pytest.mark.parametrize(
    "command",
    [
        ["python", "../candidate.py"],
        ["python3", "../../candidate.py"],
        ["python", "/tmp/candidate.py"],
        ["python3", "-"],
        ["python", "candidate.sh"],
        ["python3", "candidate"],
    ],
)
def test_unsafe_python_script_forms_are_rejected(
    monkeypatch,
    tmp_path,
    command,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()
    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "unsafe script form reached subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match="UNSAFE_COMMAND_ARGUMENT",
    ):
        agent_runner.run_candidate(command)


def test_relative_python_script_reaches_only_mocked_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()
    (workspace / "candidate.py").write_text(
        "print('candidate')\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(protected)

    observed = {}

    class Completed:
        returncode = 0

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["cwd"] = kwargs.get("cwd")
        observed["env"] = kwargs.get("env")
        observed["stdin"] = kwargs.get("stdin")
        observed["timeout"] = kwargs.get("timeout")
        observed["check"] = kwargs.get("check")
        observed["pass_fds"] = kwargs.get("pass_fds", ())
        return Completed()

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        fake_run,
    )

    rc = agent_runner.run_candidate(
        ["python", "candidate.py"]
    )

    assert rc == 0
    trusted_python = str(
        Path(agent_runner.sys.executable).resolve()
    )

    assert observed["command"][0] == trusted_python
    assert observed["command"][1] == "-I"
    assert observed["command"][2] == "-c"
    assert "/proc/self/fd/" not in " ".join(observed["command"])
    assert observed["command"][1] != "candidate.py"
    assert observed["pass_fds"] == ()
    assert observed["cwd"] == workspace.resolve()
    assert observed["timeout"] == agent_runner.TIMEOUT_SECONDS
    assert observed["check"] is False
    assert observed["env"]["HOME"] == str(
        workspace.resolve()
    )


def test_sanitized_environment_does_not_trust_parent_path(
    monkeypatch,
    tmp_path,
):
    workspace = tmp_path / "guardian-agent"
    workspace.mkdir()

    monkeypatch.setenv(
        "PATH",
        "/untrusted/fake-bin:/another/untrusted-bin",
    )

    env = agent_runner.sanitized_environment(workspace)

    assert env["PATH"] != (
        "/untrusted/fake-bin:/another/untrusted-bin"
    )

    assert "/untrusted/fake-bin" not in env["PATH"]
    assert "/another/untrusted-bin" not in env["PATH"]


def test_missing_candidate_script_is_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()
    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "missing script must never reach subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match="SCRIPT_NOT_REGULAR_FILE",
    ):
        agent_runner.run_candidate(
            ["python", "missing.py"]
        )


def test_candidate_directory_named_py_is_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()
    (workspace / "candidate.py").mkdir()
    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "directory must never reach subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match="SCRIPT_NOT_REGULAR_FILE",
    ):
        agent_runner.run_candidate(
            ["python", "candidate.py"]
        )


def test_candidate_symlink_is_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"
    outside = tmp_path / "outside.py"

    protected.mkdir()
    workspace.mkdir()

    outside.write_text(
        "print('outside')\n",
        encoding="utf-8",
    )

    (workspace / "candidate.py").symlink_to(outside)

    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "symlink must never reach subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match="SCRIPT_SYMLINK_FORBIDDEN",
    ):
        agent_runner.run_candidate(
            ["python", "candidate.py"]
        )


def test_nested_symlink_escape_is_rejected_before_subprocess(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"
    outside = tmp_path / "outside"

    protected.mkdir()
    workspace.mkdir()
    outside.mkdir()

    (outside / "candidate.py").write_text(
        "print('outside')\n",
        encoding="utf-8",
    )

    (workspace / "nested").symlink_to(
        outside,
        target_is_directory=True,
    )

    monkeypatch.chdir(protected)

    def forbidden_run(*args, **kwargs):
        raise AssertionError(
            "symlink escape must never reach subprocess"
        )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "SCRIPT_SYMLINK_FORBIDDEN"
            "|SCRIPT_OUTSIDE_WORKSPACE"
        ),
    ):
        agent_runner.run_candidate(
            ["python", "nested/candidate.py"]
        )


def test_candidate_swap_between_validation_and_open_fails_closed(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"
    outside = tmp_path / "outside.py"

    protected.mkdir()
    workspace.mkdir()

    candidate = workspace / "candidate.py"

    candidate.write_text(
        "print('validated')\n",
        encoding="utf-8",
    )

    outside.write_text(
        "print('outside')\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(protected)

    original_open = agent_runner.os.open
    swapped = {"done": False}
    subprocess_reached = {"value": False}

    def adversarial_open(path, flags, *args, **kwargs):
        path_obj = Path(path)

        if (
            not swapped["done"]
            and path_obj.name == "candidate.py"
        ):
            candidate.unlink()
            candidate.symlink_to(outside)
            swapped["done"] = True

        return original_open(
            path,
            flags,
            *args,
            **kwargs,
        )

    def forbidden_run(*args, **kwargs):
        subprocess_reached["value"] = True
        raise AssertionError(
            "TOCTOU swap reached subprocess"
        )

    monkeypatch.setattr(
        agent_runner.os,
        "open",
        adversarial_open,
    )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        (RuntimeError, OSError),
    ):
        agent_runner.run_candidate(
            ["python", "candidate.py"]
        )

    assert swapped["done"] is True
    assert subprocess_reached["value"] is False


def test_regular_file_swap_between_validation_and_open_fails_closed(
    monkeypatch,
    tmp_path,
):
    protected = tmp_path / "guardian-hunter"
    workspace = tmp_path / "guardian-agent"

    protected.mkdir()
    workspace.mkdir()

    candidate = workspace / "candidate.py"
    replacement = workspace / "replacement.py"

    candidate.write_text(
        "print('validated')\n",
        encoding="utf-8",
    )

    replacement.write_text(
        "print('replacement')\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(protected)

    original_open = agent_runner.os.open
    swapped = {"done": False}
    subprocess_reached = {"value": False}

    def adversarial_open(path, flags, *args, **kwargs):
        path_obj = Path(path)

        if (
            not swapped["done"]
            and path_obj.name == "candidate.py"
        ):
            candidate.unlink()
            replacement.replace(candidate)
            swapped["done"] = True

        return original_open(
            path,
            flags,
            *args,
            **kwargs,
        )

    def forbidden_run(*args, **kwargs):
        subprocess_reached["value"] = True
        raise AssertionError(
            "REGULAR_FILE_SWAP_REACHED_SUBPROCESS"
        )

    monkeypatch.setattr(
        agent_runner.os,
        "open",
        adversarial_open,
    )

    monkeypatch.setattr(
        agent_runner.subprocess,
        "run",
        forbidden_run,
    )

    with pytest.raises(
        (RuntimeError, OSError),
    ):
        agent_runner.run_candidate(
            ["python", "candidate.py"]
        )

    assert swapped["done"] is True
    assert subprocess_reached["value"] is False
