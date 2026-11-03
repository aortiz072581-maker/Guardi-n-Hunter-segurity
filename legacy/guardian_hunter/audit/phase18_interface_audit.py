"""
Guardian Hunter
Phase 18 Real Interface Compatibility Audit

READ-ONLY AUDIT ONLY.

This module:
- does not modify Phase 18
- does not modify Authorization Contract
- does not execute response actions
- does not invoke subprocesses
- does not enable execution

It inspects the real Phase 18 Python interfaces and compares
their public surface against the isolated authorization bridge.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PHASE18_MODULES = [
    "guardian_hunter.network.phase18_anomaly",
    "guardian_hunter.network.phase18_baseline",
    "guardian_hunter.network.phase18_case_bridge",
    "guardian_hunter.network.phase18_connection",
    "guardian_hunter.network.phase18_containment",
    "guardian_hunter.network.phase18_correlation",
    "guardian_hunter.network.phase18_decision",
    "guardian_hunter.network.phase18_diff",
    "guardian_hunter.network.phase18_dns",
    "guardian_hunter.network.phase18_evidence",
]

BRIDGE_MODULE = "guardian_hunter.authorization.phase18_bridge"

FORBIDDEN_EXECUTION_PATTERNS = {
    "os.system",
    "os.popen",
    "subprocess.Popen",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "eval",
    "exec",
    "shell=True",
}

SENSITIVE_EXECUTION_NAMES = {
    "system",
    "popen",
    "Popen",
    "call",
    "check_call",
    "check_output",
    "eval",
    "exec",
}


@dataclass(frozen=True)
class InterfaceRecord:
    module: str
    functions: tuple[str, ...]
    classes: tuple[str, ...]
    imports_ok: bool
    error: str = ""


@dataclass(frozen=True)
class AuditResult:
    passed: bool
    phase18_imports: int
    phase18_import_failures: int
    interface_records: tuple[InterfaceRecord, ...]
    bridge_import_ok: bool
    forbidden_patterns: tuple[str, ...]
    compatibility_issues: tuple[str, ...]
    safety_invariants_ok: bool


def _module_path(module_name: str) -> Path:
    relative = Path(*module_name.split(".")).with_suffix(".py")
    return PROJECT_ROOT / relative


def _public_ast_surface(path: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    tree = ast.parse(path.read_text())

    functions: list[str] = []
    classes: list[str] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                classes.append(node.name)

            for child in node.body:
                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef),
                ):
                    if not child.name.startswith("_"):
                        functions.append(
                            f"{node.name}.{child.name}"
                        )

    return tuple(sorted(functions)), tuple(sorted(classes))


def inspect_phase18_interfaces() -> tuple[InterfaceRecord, ...]:
    records: list[InterfaceRecord] = []

    for module_name in PHASE18_MODULES:
        path = _module_path(module_name)

        try:
            functions, classes = _public_ast_surface(path)
        except Exception as exc:
            records.append(
                InterfaceRecord(
                    module=module_name,
                    functions=(),
                    classes=(),
                    imports_ok=False,
                    error=f"AST: {exc!r}",
                )
            )
            continue

        try:
            importlib.import_module(module_name)

            records.append(
                InterfaceRecord(
                    module=module_name,
                    functions=functions,
                    classes=classes,
                    imports_ok=True,
                )
            )

        except Exception as exc:
            records.append(
                InterfaceRecord(
                    module=module_name,
                    functions=functions,
                    classes=classes,
                    imports_ok=False,
                    error=f"IMPORT: {exc!r}",
                )
            )

    return tuple(records)


def inspect_bridge() -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    try:
        bridge = importlib.import_module(BRIDGE_MODULE)
    except Exception as exc:
        return False, (f"bridge import failed: {exc!r}",)

    required = [
        "Phase18AuthorizationBridge",
        "Phase18AuthorizationResult",
        "safety_invariants_hold",
    ]

    for name in required:
        if not hasattr(bridge, name):
            issues.append(f"bridge missing required symbol: {name}")

    try:
        signature = inspect.signature(
            bridge.Phase18AuthorizationBridge.authorize_phase18_event
        )

        required_params = {"self", "event"}

        if not required_params.issubset(signature.parameters):
            issues.append(
                "authorize_phase18_event missing required parameters"
            )

    except Exception as exc:
        issues.append(
            f"bridge signature inspection failed: {exc!r}"
        )

    return not issues, tuple(issues)


def scan_forbidden_execution_patterns() -> tuple[str, ...]:
    """
    Detect explicit dangerous execution constructs structurally.

    IMPORTANT:
    Do not use substring matching here.

    For example:
        execution_allowed
        execute_response
        real_execution_blocked

    must NOT be interpreted as exec().

    The audit therefore uses AST inspection for actual calls and
    shell=True keyword arguments.
    """

    findings: list[str] = []

    for module_name in PHASE18_MODULES:
        path = _module_path(module_name)

        if not path.exists():
            findings.append(f"missing file: {path}")
            continue

        try:
            tree = ast.parse(path.read_text())
        except Exception as exc:
            findings.append(
                f"{module_name}: AST_PARSE_ERROR: {exc!r}"
            )
            continue

        for node in ast.walk(tree):

            if isinstance(node, ast.Call):

                # Direct calls:
                # exec(...)
                # eval(...)
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval"}:
                        findings.append(
                            f"{module_name}: call to {node.func.id}"
                        )

                # Attribute calls:
                # os.system(...)
                # os.popen(...)
                # subprocess.Popen(...)
                # subprocess.call(...)
                # subprocess.check_call(...)
                # subprocess.check_output(...)
                elif isinstance(node.func, ast.Attribute):
                    attr = node.func.attr

                    if attr in {
                        "system",
                        "popen",
                        "Popen",
                        "call",
                        "check_call",
                        "check_output",
                    }:
                        findings.append(
                            f"{module_name}: call to {attr}"
                        )

                # shell=True
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        findings.append(
                            f"{module_name}: shell=True"
                        )

    return tuple(sorted(set(findings)))


def inspect_ast_sensitive_calls() -> tuple[str, ...]:
    findings: list[str] = []

    for module_name in PHASE18_MODULES:
        path = _module_path(module_name)

        if not path.exists():
            continue

        try:
            tree = ast.parse(path.read_text())
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            name = None

            if isinstance(node.func, ast.Name):
                name = node.func.id

            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr

            if name in SENSITIVE_EXECUTION_NAMES:
                findings.append(
                    f"{module_name}: call to {name}"
                )

    return tuple(sorted(set(findings)))


def inspect_bridge_dependencies() -> tuple[str, ...]:
    issues: list[str] = []

    try:
        source = (
            PROJECT_ROOT
            / "guardian_hunter"
            / "authorization"
            / "phase18_bridge.py"
        ).read_text()
    except Exception as exc:
        return (f"bridge source unavailable: {exc!r}",)

    forbidden_bridge_refs = [
        "subprocess",
        "os.system",
        "os.popen",
        "Popen",
        "check_call",
        "check_output",
        "shell=True",
    ]

    for item in forbidden_bridge_refs:
        if item in source:
            issues.append(
                f"bridge contains execution reference: {item}"
            )

    return tuple(sorted(set(issues)))


def inspect_safety_invariants() -> bool:
    try:
        from guardian_hunter.authorization.contract import (
            READ_ONLY,
            DRY_RUN,
            REAL_EXECUTION_BLOCKED,
            HUMAN_REVIEW_REQUIRED,
            RESPONSE_LOCKED,
        )

        from guardian_hunter.authorization.phase18_bridge import (
            safety_invariants_hold,
        )

        return (
            READ_ONLY is True
            and DRY_RUN is True
            and REAL_EXECUTION_BLOCKED is True
            and HUMAN_REVIEW_REQUIRED is True
            and RESPONSE_LOCKED is True
            and safety_invariants_hold() is True
        )

    except Exception:
        return False


def run_audit() -> AuditResult:
    records = inspect_phase18_interfaces()

    import_failures = sum(
        not record.imports_ok
        for record in records
    )

    bridge_ok, bridge_issues = inspect_bridge()

    forbidden = scan_forbidden_execution_patterns()

    sensitive_calls = inspect_ast_sensitive_calls()

    bridge_dependencies = inspect_bridge_dependencies()

    compatibility_issues = list(bridge_issues)
    compatibility_issues.extend(bridge_dependencies)

    # Sensitive execution calls are reported for human review.
    # They do not automatically indicate a bypass because some
    # Phase 18 collection modules legitimately use read-only
    # subprocess calls.
    compatibility_issues.extend(
        f"SENSITIVE_CALL_REVIEW: {item}"
        for item in sensitive_calls
    )

    safety_ok = inspect_safety_invariants()

    passed = (
        len(records) == len(PHASE18_MODULES)
        and import_failures == 0
        and bridge_ok
        and not forbidden
        and safety_ok
    )

    return AuditResult(
        passed=passed,
        phase18_imports=len(PHASE18_MODULES) - import_failures,
        phase18_import_failures=import_failures,
        interface_records=records,
        bridge_import_ok=bridge_ok,
        forbidden_patterns=forbidden,
        compatibility_issues=tuple(
            sorted(set(compatibility_issues))
        ),
        safety_invariants_ok=safety_ok,
    )


def print_report(result: AuditResult) -> None:
    print("=" * 62)
    print("PHASE 18 REAL INTERFACE COMPATIBILITY AUDIT")
    print("=" * 62)

    print()
    print(
        f"PHASE 18 MODULES: "
        f"{result.phase18_imports}/{len(PHASE18_MODULES)} OK"
    )

    print(
        f"IMPORT FAILURES: "
        f"{result.phase18_import_failures}"
    )

    print()
    print("INTERFACE SURFACE")

    for record in result.interface_records:
        print()
        print(record.module)
        print(f"  IMPORT: {'OK' if record.imports_ok else 'FAIL'}")

        if record.classes:
            print(
                "  CLASSES:",
                ", ".join(record.classes),
            )
        else:
            print("  CLASSES: NONE")

        if record.functions:
            print(
                "  FUNCTIONS:",
                ", ".join(record.functions),
            )
        else:
            print("  FUNCTIONS: NONE")

        if record.error:
            print("  ERROR:", record.error)

    print()
    print(
        "BRIDGE IMPORT:",
        "OK" if result.bridge_import_ok else "FAIL",
    )

    print()
    print(
        "FORBIDDEN EXECUTION PATTERNS:",
        len(result.forbidden_patterns),
    )

    if result.forbidden_patterns:
        for item in result.forbidden_patterns:
            print("  -", item)

    print()
    print("COMPATIBILITY / REVIEW ITEMS:")

    if result.compatibility_issues:
        for item in result.compatibility_issues:
            print("  -", item)
    else:
        print("  NONE")

    print()
    print(
        "SAFETY INVARIANTS:",
        "OK" if result.safety_invariants_ok else "FAIL",
    )

    print()
    print(
        "AUDIT STATE:",
        "COMPATIBLE" if result.passed else "REVIEW_REQUIRED",
    )

    print("=" * 62)


if __name__ == "__main__":
    result = run_audit()
    print_report(result)

    # The audit only fails automatically for:
    # - import failure
    # - missing bridge
    # - explicit forbidden execution pattern
    # - broken safety invariants
    #
    # Ordinary subprocess collection calls are reported separately
    # as REVIEW items rather than being misclassified as bypasses.

    raise SystemExit(0 if result.passed else 1)
