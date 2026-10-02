"""Guardian Gate — Git candidate checker."""

from __future__ import annotations

import subprocess
from pathlib import Path

from guardian_hunter.gate.core import evaluate_candidate


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("GIT_CHECK_FAILED")
    return result.stdout.strip()


def changed_files() -> list[str]:
    tracked = git("diff", "--name-only", "HEAD").splitlines()
    untracked = git(
        "ls-files",
        "--others",
        "--exclude-standard",
    ).splitlines()

    return sorted(set(tracked + untracked))


def safe_path(path: str) -> bool:
    p = Path(path)

    return (
        bool(path)
        and not p.is_absolute()
        and ".." not in p.parts
        and "\x00" not in path
    )


def main() -> int:
    try:
        head = git("rev-parse", "HEAD")
        branch = git("branch", "--show-current")
        files = changed_files()

        if not all(safe_path(path) for path in files):
            print("GUARDIAN GATE: FAIL")
            print("REASON: UNSAFE_PATH")
            return 1

        result = evaluate_candidate(files)

        print("=== GUARDIAN GATE ===")
        print("HEAD:", head)
        print("BRANCH:", branch)
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
        print("GUARDIAN GATE: FAIL")
        print("REASON:", type(exc).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
