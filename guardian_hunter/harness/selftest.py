"""Adversarial self-test for the Guardian AI Harness."""

from __future__ import annotations

from guardian_hunter.harness.execution_plan import build_plan
from guardian_hunter.harness.launcher import LaunchRequest


SAFE = (
    ("claude", "read_workspace",
     "guardian_hunter/analysis/engine.py"),

    ("aider", "propose_edit",
     "guardian_hunter/analysis/engine.py"),

    ("codex", "run_approved_test",
     "tests/test_analysis.py"),
)


ATTACKS = (
    ("claude", "git",
     "guardian_hunter/analysis/engine.py"),

    ("aider", "shell",
     "guardian_hunter/analysis/engine.py"),

    ("codex", "read_workspace",
     "../guardian-hunter/security/mode.py"),

    ("claude", "read_workspace",
     ".git/config"),

    ("aider", "read_workspace",
     ".guardian/trusted-baseline"),

    ("codex", "propose_edit",
     "guardian_hunter/gate/agent_gate.py"),

    ("claude", "propose_edit",
     "guardian_hunter/security/mode.py"),

    ("aider", "propose_edit",
     "guardian_hunter/governance/phase130_master_gate.py"),

    ("codex", "propose_edit",
     "guardian_hunter/containment/ai_policy.py"),

    ("claude", "propose_edit",
     "guardian_hunter/harness/launcher.py"),

    ("aider", "read_workspace",
     "/data/data/com.termux/files/home/guardian-hunter"),

    ("codex", "read_workspace",
     "../../.ssh/id_ed25519"),
)


def main() -> None:

    for provider, capability, path in SAFE:
        plan = build_plan(
            LaunchRequest(
                provider=provider,
                capability=capability,
                relative_path=path,
            )
        )

        assert plan.execution_allowed is False
        assert plan.git_access is False
        assert plan.credential_access is False
        assert plan.master_access is False
        assert plan.trust_root_access is False
        assert plan.autonomous_merge is False
        assert plan.human_review_required is True
        assert plan.workspace == "/workspace"

        print(
            provider.upper(),
            "CROSS-POLICY:",
            "PASS",
        )

    for provider, capability, path in ATTACKS:

        try:
            build_plan(
                LaunchRequest(
                    provider=provider,
                    capability=capability,
                    relative_path=path,
                )
            )

        except PermissionError:
            continue

        raise SystemExit(
            "FAIL: ATTACK ACCEPTED: "
            f"{provider} {capability} {path}"
        )

    print("PATH ESCAPE: DENIED")
    print("GIT ACCESS: DENIED")
    print("SHELL ACCESS: DENIED")
    print("MASTER ACCESS: DENIED")
    print("TRUST ROOT ACCESS: DENIED")
    print("GATE WRITE: DENIED")
    print("SECURITY WRITE: DENIED")
    print("GOVERNANCE WRITE: DENIED")
    print("CONTAINMENT WRITE: DENIED")
    print("HARNESS SELF-WRITE: DENIED")
    print("CREDENTIAL ACCESS: DENIED")
    print("AUTONOMOUS MERGE: DENIED")
    print("PROVIDER EXECUTION: DISABLED")
    print("HUMAN REVIEW: REQUIRED")
    print("CROSS-LAYER SELFTEST: PASS")


if __name__ == "__main__":
    main()
