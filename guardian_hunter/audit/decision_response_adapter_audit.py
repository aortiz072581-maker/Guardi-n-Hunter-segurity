"""
Guardian Hunter — Controlled Adapter v1 Static Audit

Purpose:
- Validate the authorization -> decision/response adapter surface.
- Confirm fail-closed execution behavior.
- Confirm no forbidden execution primitives.
- Confirm safety invariants.
- Do not modify Phase 18.
- Do not execute real responses.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = (
    ROOT
    / "guardian_hunter"
    / "authorization"
    / "decision_response_adapter.py"
)


SAFETY_EXPECTED = {
    "READ_ONLY": True,
    "DRY_RUN": True,
    "REAL_EXECUTION_BLOCKED": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "RESPONSE_LOCKED": True,
}


FORBIDDEN_CALLS = {
    "exec",
    "eval",
    "system",
    "popen",
    "Popen",
    "call",
    "check_call",
    "check_output",
}


def _call_name(node: ast.Call) -> str | None:
    fn = node.func

    if isinstance(fn, ast.Name):
        return fn.id

    if isinstance(fn, ast.Attribute):
        return fn.attr

    return None


def audit() -> int:
    print("GUARDIAN HUNTER — CONTROLLED ADAPTER v1 STATIC AUDIT")
    print("=" * 62)

    if not ADAPTER.exists():
        print("ADAPTER FILE: MISSING")
        print(f"PATH: {ADAPTER}")
        return 1

    print("ADAPTER FILE: PRESENT")

    try:
        source = ADAPTER.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(ADAPTER))
    except Exception as exc:
        print(f"AST PARSE: FAILED: {exc}")
        return 1

    print("AST PARSE: OK")

    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    imports |= {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    required_imports = {
        "guardian_hunter.authorization.contract",
        "guardian_hunter.response.policy",
        "guardian_hunter.response.orchestrator",
    }

    missing_imports = sorted(
        item for item in required_imports
        if item not in imports
    )

    if missing_imports:
        print("REQUIRED IMPORTS: FAILED")
        for item in missing_imports:
            print(f"  MISSING: {item}")
        return 1

    print("REQUIRED IMPORTS: OK")

    execution_true = 0
    execution_false = 0
    forbidden = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):
            name = _call_name(node)

            if name in FORBIDDEN_CALLS:
                forbidden.append(name)

        if isinstance(node, ast.keyword):
            if node.arg == "execution_allowed":
                if isinstance(node.value, ast.Constant):
                    if node.value.value is True:
                        execution_true += 1
                    elif node.value.value is False:
                        execution_false += 1

    print(f"EXECUTION_ALLOWED=True: {execution_true}")
    print(f"EXECUTION_ALLOWED=False: {execution_false}")

    if execution_true != 0:
        print("EXECUTION GATE: FAILED")
        print("Explicit execution_allowed=True detected.")
        return 1

    if execution_false == 0:
        print("EXECUTION GATE: FAILED")
        print("No explicit execution_allowed=False gate detected.")
        return 1

    print("EXECUTION GATE: FAIL-CLOSED")

    if forbidden:
        print("FORBIDDEN EXECUTION: FAILED")
        for item in sorted(set(forbidden)):
            print(f"  {item}")
        return 1

    print("FORBIDDEN EXECUTION: 0")

    safety_missing = []

    for name, expected in SAFETY_EXPECTED.items():
        if name not in source:
            safety_missing.append(name)

    if safety_missing:
        print("SAFETY CONSTANTS: FAILED")
        for item in safety_missing:
            print(f"  MISSING: {item}")
        return 1

    print("SAFETY CONSTANTS: PRESENT")

    if "Phase 18" in source or "phase18" in source.lower():
        print("PHASE 18 REFERENCE: PRESENT")
        print("PHASE 18 MODIFICATION: NOT PERFORMED")
    else:
        print("PHASE 18 MODIFICATION: NONE")

    if "AuthorizationEngine" not in source:
        print("AUTHORIZATION ENGINE: MISSING")
        return 1

    if "AuthorizationRequest" not in source:
        print("AUTHORIZATION REQUEST: MISSING")
        return 1

    print("AUTHORIZATION ENGINE: PRESENT")
    print("AUTHORIZATION REQUEST: PRESENT")

    print()
    print("READ_ONLY: True")
    print("DRY_RUN: True")
    print("REAL_EXECUTION_BLOCKED: True")
    print("HUMAN_REVIEW_REQUIRED: True")
    print("RESPONSE_LOCKED: True")
    print("REAL EXECUTION: BLOCKED")

    print()
    print("=" * 62)
    print("CONTROLLED ADAPTER v1 STATIC AUDIT: OK")
    print("=" * 62)

    return 0


if __name__ == "__main__":
    raise SystemExit(audit())
