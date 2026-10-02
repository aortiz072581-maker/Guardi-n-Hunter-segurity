"""Guardian Gate — evaluate isolated agent workspace.

Runs from the protected Guardian Hunter workspace.
The candidate cannot choose its trusted baseline.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from guardian_hunter.gate.core import evaluate_candidate


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError("GIT_OPERATION_FAILED")

    return result.stdout.strip()


def main() -> int:
    try:
        protected = Path.cwd().resolve()
        agent = protected.parent / "guardian-agent"
        baseline_file = protected / ".guardian" / "trusted-baseline"

        if not baseline_file.is_file():
            raise RuntimeError("TRUSTED_BASELINE_MISSING")

        if not agent.is_dir():
            raise RuntimeError("AGENT_WORKSPACE_MISSING")

        baseline = baseline_file.read_text().strip()

        if len(baseline) != 40:
            raise RuntimeError("INVALID_BASELINE")

        # Baseline must exist in protected repository.
        run_git(protected, "cat-file", "-e", f"{baseline}^{{commit}}")

        # Protected master itself must still equal trusted baseline.
        protected_head = run_git(protected, "rev-parse", "HEAD")

        if protected_head != baseline:
            raise RuntimeError("PROTECTED_HEAD_BASELINE_MISMATCH")

        # Candidate changes are derived independently from Git.
        diff = run_git(
            agent,
            "diff",
            "--name-only",
            baseline,
        )

        untracked = run_git(
            agent,
            "ls-files",
            "--others",
            "--exclude-standard",
        )

        files = sorted(
            set(
                line
                for block in (diff, untracked)
                for line in block.splitlines()
                if line
            )
        )

        result = evaluate_candidate(files)

        print("=== GUARDIAN AGENT GATE ===")
        print("BASELINE:", baseline)
        print("PROTECTED HEAD:", protected_head)
        print("CHANGED:", len(files))

        for path in files:
            print(" -", path)

        print("RESULT:", "PASS" if result.passed else "FAIL")
        print("REASON:", result.reason)
        print(
            "HUMAN REVIEW REQUIRED:",
            result.human_review_required,
        )
        print(
            "AGENT MERGE ALLOWED:",
            result.agent_merge_allowed,
        )

        return 0 if result.passed else 1

    except Exception as exc:
        print("=== GUARDIAN AGENT GATE ===")
        print("RESULT: FAIL")
        print("REASON:", str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
