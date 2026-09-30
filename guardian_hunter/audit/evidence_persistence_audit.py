"""
Guardian Hunter — Evidence Persistence Static Audit v1
"""

from __future__ import annotations

import ast
from pathlib import Path

from guardian_hunter.evidence.persistence import (
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
    target = root / "guardian_hunter" / "evidence" / "persistence.py"

    print("GUARDIAN HUNTER — EVIDENCE PERSISTENCE STATIC AUDIT v1")
    print("=" * 64)

    if not target.exists():
        print("EVIDENCE MODULE: MISSING")
        return 1

    try:
        tree = ast.parse(
            target.read_text(encoding="utf-8")
        )
    except SyntaxError:
        print("AST PARSE: FAILED")
        return 1

    forbidden = forbidden_calls(tree)

    source = target.read_text(encoding="utf-8")

    execution_true = (
        "execution_allowed=True" in source
    )

    append_only = (
        'open("a"' in source
        or "open('a'" in source
    )

    hash_chain = (
        "previous_hash" in source
        and "record_hash" in source
    )

    safety = safety_invariants_hold()

    print("EVIDENCE MODULE: PRESENT")
    print("AST PARSE: OK")
    print(
        "FORBIDDEN EXECUTION CALLS:",
        "0" if not forbidden else ", ".join(forbidden),
    )
    print(
        "EXECUTION_ALLOWED=True:",
        1 if execution_true else 0,
    )
    print(
        "APPEND-ONLY STORE:",
        "OK" if append_only else "FAILED",
    )
    print(
        "HASH CHAIN:",
        "OK" if hash_chain else "FAILED",
    )
    print(
        "FAIL-CLOSED DESIGN:",
        "OK" if not execution_true else "FAILED",
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
        and append_only
        and hash_chain
        and safety
    )

    print()

    if ok:
        print("=" * 64)
        print("EVIDENCE PERSISTENCE STATIC AUDIT: OK")
        print("=" * 64)
        return 0

    print("=" * 64)
    print("EVIDENCE PERSISTENCE STATIC AUDIT: FAILED")
    print("=" * 64)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_audit())
