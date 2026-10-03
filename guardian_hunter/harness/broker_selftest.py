"""Adversarial tests for the Guardian provider broker."""

from __future__ import annotations

from guardian_hunter.harness.broker import (
    CREDENTIAL_NAMES,
    prepare,
    sanitized_environment,
)
from guardian_hunter.harness.launcher import LaunchRequest


def main() -> None:
    for provider in ("claude", "aider", "codex"):
        result = prepare(
            LaunchRequest(
                provider=provider,
                capability="read_workspace",
                relative_path="guardian_hunter/analysis/engine.py",
            )
        )

        assert result.dry_run is True
        assert result.executed is False
        assert result.credentials_present is False
        assert result.git_available is False
        assert result.workspace == "/workspace"
        assert result.timeout_seconds == 300

        print(provider.upper(), "BROKER DRY-RUN: PASS")

    env = sanitized_environment()

    for secret in CREDENTIAL_NAMES:
        assert secret not in env

    print("CREDENTIAL SANITIZATION: PASS")

    attacks = (
        ("claude", "git", ".git/config"),
        ("aider", "shell", "../guardian-hunter"),
        ("codex", "propose_edit",
         "guardian_hunter/gate/agent_gate.py"),
        ("claude", "propose_edit",
         "guardian_hunter/harness/broker.py"),
        ("aider", "read_workspace",
         ".guardian/trusted-baseline"),
    )

    for provider, capability, path in attacks:
        try:
            prepare(
                LaunchRequest(
                    provider=provider,
                    capability=capability,
                    relative_path=path,
                )
            )
        except PermissionError:
            continue

        raise SystemExit(
            f"FAIL: broker accepted attack: "
            f"{provider} {capability} {path}"
        )

    try:
        prepare(
            LaunchRequest(
                provider="codex",
                capability="read_workspace",
                relative_path="guardian_hunter/analysis/engine.py",
            ),
            dry_run=False,
        )
    except PermissionError:
        pass
    else:
        raise SystemExit(
            "FAIL: real execution unexpectedly enabled"
        )

    print("REAL EXECUTION BYPASS: DENIED")
    print("PROTECTED PATH BYPASS: DENIED")
    print("BROKER SELFTEST: PASS")


if __name__ == "__main__":
    main()
