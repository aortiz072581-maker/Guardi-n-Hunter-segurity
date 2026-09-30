"""
Guardian Hunter — Self-Integrity Static Audit v1

Audit only.
No project mutation.
No external command execution.
"""

from __future__ import annotations

import ast
from pathlib import Path

from guardian_hunter.integrity.self_integrity import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    safety_invariants_hold,
)


FORBIDDEN_CALLS = {
    "exec",
    "eval",
    "system",
    "popen",
    "Popen",
    "call",
    "check_call",
    "check_output",
    "run",
}


def _forbidden_calls(tree: ast.AST) -> list[str]:
    found = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        if isinstance(func, ast.Name):
            if func.id in FORBIDDEN_CALLS:
                found.append(func.id)

        elif isinstance(func, ast.Attribute):
            if func.attr in FORBIDDEN_CALLS:
                found.append(func.attr)

    return sorted(set(found))


def run_audit() -> int:
    root = Path(__file__).resolve().parents[2]
    target = root / "guardian_hunter" / "integrity" / "self_integrity.py"

    print("GUARDIAN HUNTER — SELF-INTEGRITY STATIC AUDIT v1")
    print("=" * 64)

    if not target.exists():
        print("INTEGRITY MODULE: MISSING")
        return 1

    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError:
        print("AST PARSE: FAILED")
        return 1

    forbidden = _forbidden_calls(tree)

    execution_true = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            left = node.left

            if isinstance(left, ast.Name):
                if left.id == "execution_allowed":
                    for comparator in node.comparators:
                        if (
                            isinstance(comparator, ast.Constant)
                            and comparator.value is True
                        ):
                            execution_true += 1

    print("INTEGRITY MODULE: PRESENT")
    print("AST PARSE: OK")
    print("FORBIDDEN EXECUTION CALLS:",
          "0" if not forbidden else ", ".join(forbidden))
    print("EXECUTION_ALLOWED=True:", execution_true)
    print(
        "FAIL-CLOSED DESIGN:",
        "OK" if execution_true == 0 else "FAILED",
    )
    print(
        "SAFETY INVARIANTS:",
        "OK" if safety_invariants_hold() else "FAILED",
    )

    print()
    print("READ_ONLY:", READ_ONLY)
    print("DRY_RUN:", DRY_RUN)
    print("REAL_EXECUTION_BLOCKED:", REAL_EXECUTION_BLOCKED)
    print("HUMAN_REVIEW_REQUIRED:", HUMAN_REVIEW_REQUIRED)
    print("RESPONSE_LOCKED:", RESPONSE_LOCKED)
    print("REAL EXECUTION: BLOCKED")

    ok = (
        not forbidden
        and execution_true == 0
        and safety_invariants_hold()
    )

    print()

    if ok:
        print("=" * 64)
        print("SELF-INTEGRITY STATIC AUDIT: OK")
        print("=" * 64)
        return 0

    print("=" * 64)
    print("SELF-INTEGRITY STATIC AUDIT: FAILED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_audit())
