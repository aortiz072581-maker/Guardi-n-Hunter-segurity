"""
Guardian Hunter — Incident State & Recovery Static Audit v1
"""

from __future__ import annotations

import ast
from pathlib import Path

from guardian_hunter.incident.state import (
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


def forbidden_calls(tree: ast.AST) -> list[str]:
    found: list[str] = []

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
    target = root / "guardian_hunter" / "incident" / "state.py"

    print(
        "GUARDIAN HUNTER — INCIDENT STATE & RECOVERY "
        "STATIC AUDIT v1"
    )
    print("=" * 64)

    if not target.exists():
        print("INCIDENT MODULE: MISSING")
        return 1

    source = target.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print("AST PARSE: FAILED")
        return 1

    forbidden = forbidden_calls(tree)

    execution_true = (
        "execution_allowed=True" in source
    )

    state_markers = [
        "NEW",
        "TRIAGED",
        "AUTHORIZED",
        "CONTAINMENT_PLANNED",
        "CONTAINMENT_REVIEW",
        "RECOVERY_PLANNED",
        "RECOVERY_REVIEW",
        "RESOLVED",
        "FAILED",
        "LOCKED",
    ]

    states_ok = all(
        marker in source
        for marker in state_markers
    )

    fail_closed_present = (
        "fail_closed" in source
        and "execution_allowed is False" in source
    )

    safety = safety_invariants_hold()

    print("INCIDENT MODULE: PRESENT")
    print("AST PARSE: OK")
    print(
        "STATE MODEL:",
        "OK" if states_ok else "FAILED",
    )
    print(
        "FORBIDDEN EXECUTION CALLS:",
        "0" if not forbidden else ", ".join(forbidden),
    )
    print(
        "EXECUTION_ALLOWED=True:",
        1 if execution_true else 0,
    )
    print(
        "FAIL-CLOSED:",
        "OK"
        if fail_closed_present and not execution_true
        else "FAILED",
    )
    print(
        "SAFETY INVARIANTS:",
        "OK" if safety else "FAILED",
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
        and not execution_true
        and states_ok
        and fail_closed_present
        and safety
    )

    print()

    if ok:
        print("=" * 64)
        print("INCIDENT STATE & RECOVERY STATIC AUDIT: OK")
        print("=" * 64)
        return 0

    print("=" * 64)
    print("INCIDENT STATE & RECOVERY STATIC AUDIT: FAILED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_audit())
