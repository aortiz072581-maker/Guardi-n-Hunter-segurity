"""Guardian Gate — detached candidate workspace evaluator."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from guardian_hunter.gate.core import evaluate_candidate


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("PROTECTED_GIT_OPERATION_FAILED")
    return result.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(path: str) -> bool:
    candidate = Path(path)
    return (
        bool(path)
        and not candidate.is_absolute()
        and ".." not in candidate.parts
        and "\x00" not in path
    )


def baseline_files(
    protected: Path,
    baseline: str,
) -> dict[str, str]:
    raw = git(
        protected,
        "ls-tree",
        "-r",
        "--name-only",
        "-z",
        baseline,
    )

    names = [
        item.decode("utf-8")
        for item in raw.split(b"\0")
        if item
    ]

    result: dict[str, str] = {}

    for name in names:
        if not safe_relative(name):
            raise RuntimeError("UNSAFE_BASELINE_PATH")

        data = git(
            protected,
            "show",
            f"{baseline}:{name}",
        )
        result[name] = sha256_bytes(data)

    return result


def candidate_files(agent: Path) -> dict[str, str]:
    result: dict[str, str] = {}

    for path in agent.rglob("*"):
        if path.is_symlink():
            raise RuntimeError("SYMLINK_FORBIDDEN")

        if not path.is_file():
            continue

        relative = path.relative_to(agent).as_posix()

        if not safe_relative(relative):
            raise RuntimeError("UNSAFE_CANDIDATE_PATH")

        result[relative] = sha256_file(path)

    return result


def main() -> int:
    try:
        protected = Path.cwd().resolve()
        agent = (protected.parent / "guardian-agent").resolve()
        baseline_path = (
            protected / ".guardian" / "trusted-baseline"
        )

        if not baseline_path.is_file():
            raise RuntimeError("TRUSTED_BASELINE_MISSING")

        if not agent.is_dir():
            raise RuntimeError("AGENT_WORKSPACE_MISSING")

        if (agent / ".git").exists():
            raise RuntimeError("AGENT_GIT_FORBIDDEN")

        baseline = baseline_path.read_text().strip()

        if len(baseline) != 40:
            raise RuntimeError("INVALID_BASELINE")

        protected_head = (
            git(protected, "rev-parse", "HEAD")
            .decode()
            .strip()
        )

        if protected_head != baseline:
            raise RuntimeError(
                "PROTECTED_HEAD_BASELINE_MISMATCH"
            )

        expected = baseline_files(protected, baseline)
        current = candidate_files(agent)

        expected_names = set(expected)
        current_names = set(current)

        added = current_names - expected_names
        deleted = expected_names - current_names

        modified = {
            name
            for name in expected_names & current_names
            if expected[name] != current[name]
        }

        changed = sorted(added | deleted | modified)

        result = evaluate_candidate(changed)

        print("=== GUARDIAN DETACHED AGENT GATE ===")
        print("BASELINE:", baseline)
        print("EXPECTED FILES:", len(expected))
        print("CANDIDATE FILES:", len(current))
        print("ADDED:", len(added))
        print("MODIFIED:", len(modified))
        print("DELETED:", len(deleted))
        print("CHANGED:", len(changed))

        for name in changed:
            print(" -", name)

        print(
            "RESULT:",
            "PASS" if result.passed else "FAIL",
        )
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
        print("=== GUARDIAN DETACHED AGENT GATE ===")
        print("RESULT: FAIL")
        print("REASON:", str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
