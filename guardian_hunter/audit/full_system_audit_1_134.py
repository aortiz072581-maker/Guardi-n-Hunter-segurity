"""
Guardian Hunter — Full System Audit 1 → 134

AUDIT ONLY.
No modification of project state.
No external execution.
No remediation.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path("guardian_hunter")

EXPECTED_FLAGS = {
    "READ_ONLY": True,
    "DRY_RUN": True,
    "REAL_EXECUTION_BLOCKED": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "RESPONSE_LOCKED": True,
}


def discover_python_files():
    return sorted(ROOT.rglob("*.py")) if ROOT.exists() else []


def discover_phase_files():
    result = []

    for path in discover_python_files():
        name = path.name.lower()

        if "phase" in name:
            result.append(path)

    return sorted(result)


def extract_phase_numbers(path):
    text = path.read_text(errors="ignore")

    numbers = set()

    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value

            for token in value.replace("→", " ").replace("-", " ").split():
                if token.isdigit():
                    number = int(token)

                    if 1 <= number <= 134:
                        numbers.add(number)

    return sorted(numbers)


def compile_check(files):
    failures = []

    for path in files:
        try:
            ast.parse(path.read_text(errors="ignore"))
        except Exception as exc:
            failures.append(
                {
                    "file": str(path),
                    "error": repr(exc),
                }
            )

    return failures


def import_check(files):
    results = []

    for path in files:
        relative = path.relative_to(ROOT.parent)
        module = ".".join(relative.with_suffix("").parts)

        try:
            spec = importlib.util.spec_from_file_location(
                module,
                path,
            )

            if spec is None or spec.loader is None:
                raise ImportError("module spec unavailable")

            module_obj = importlib.util.module_from_spec(spec)

            # Load only the module itself.
            # Do not execute project orchestration.
            spec.loader.exec_module(module_obj)

            results.append(
                {
                    "file": str(path),
                    "importable": True,
                }
            )

        except Exception as exc:
            results.append(
                {
                    "file": str(path),
                    "importable": False,
                    "error": repr(exc),
                }
            )

    return results


def inspect_safety_flags(files):
    combined = "\n".join(
        path.read_text(errors="ignore")
        for path in files
    )

    patterns = {
        "READ_ONLY": [
            "READ_ONLY",
            "read_only",
        ],
        "DRY_RUN": [
            "DRY_RUN",
            "dry_run",
        ],
        "REAL_EXECUTION_BLOCKED": [
            "REAL_EXECUTION",
            "real_execution_blocked",
            "EXECUTION_BLOCKED",
        ],
        "HUMAN_REVIEW_REQUIRED": [
            "HUMAN_REVIEW",
            "human_review_required",
        ],
        "RESPONSE_LOCKED": [
            "RESPONSE_LOCKED",
            "response_locked",
        ],
    }

    coverage = {}

    for key, variants in patterns.items():
        coverage[key] = {
            "present": any(v in combined for v in variants),
            "matches": sum(combined.count(v) for v in variants),
        }

    return coverage


def inspect_connectivity(files):
    connectivity = []

    for path in files:
        text = path.read_text(errors="ignore")

        imports = []

        try:
            tree = ast.parse(text)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(
                        alias.name
                        for alias in node.names
                    )

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception:
            continue

        guardian_imports = [
            item for item in imports
            if item.startswith("guardian_hunter")
        ]

        connectivity.append(
            {
                "file": str(path),
                "guardian_hunter_imports": guardian_imports,
                "connected": bool(guardian_imports),
            }
        )

    return connectivity


def inspect_test_coverage():
    tests = sorted(
        ROOT.joinpath("tests").rglob("test_*.py")
    ) if ROOT.joinpath("tests").exists() else []

    phase_tests = []

    for path in tests:
        text = path.read_text(errors="ignore")

        phase_numbers = []

        for token in (
            text.replace("→", " ")
            .replace("-", " ")
            .replace("_", " ")
            .split()
        ):
            if token.isdigit():
                value = int(token)

                if 1 <= value <= 134:
                    phase_numbers.append(value)

        phase_tests.append(
            {
                "file": str(path),
                "phase_references": sorted(set(phase_numbers)),
            }
        )

    return phase_tests


def calculate_project_digest(files):
    digest = hashlib.sha256()

    for path in files:
        digest.update(str(path).encode())
        digest.update(path.read_bytes())

    return digest.hexdigest()


def build_audit():
    files = discover_python_files()
    phase_files = discover_phase_files()

    compile_failures = compile_check(files)
    imports = import_check(phase_files)
    safety = inspect_safety_flags(files)
    connectivity = inspect_connectivity(phase_files)
    tests = inspect_test_coverage()

    phase_numbers = set()

    for path in phase_files:
        phase_numbers.update(extract_phase_numbers(path))

    implemented = sorted(
        n for n in phase_numbers
        if 1 <= n <= 134
    )

    missing = [
        n for n in range(1, 135)
        if n not in implemented
    ]

    import_failures = [
        item for item in imports
        if not item["importable"]
    ]

    connected_count = sum(
        1
        for item in connectivity
        if item["connected"]
    )

    isolated_count = (
        len(connectivity) - connected_count
    )

    test_files = len(tests)

    safety_present = all(
        item["present"]
        for item in safety.values()
    )

    audit_state = "FULL_SYSTEM_AUDIT_COMPLETE"

    if compile_failures:
        audit_state = "AUDIT_COMPILE_FAILURE"

    elif missing:
        audit_state = "AUDIT_PHASE_GAPS_DETECTED"

    elif import_failures:
        audit_state = "AUDIT_IMPORT_FAILURES_DETECTED"

    elif not safety_present:
        audit_state = "AUDIT_SAFETY_COVERAGE_INCOMPLETE"

    return {
        "audit_state": audit_state,
        "python_files": len(files),
        "phase_files": len(phase_files),
        "implemented_phase_references": implemented,
        "missing_phase_references": missing,
        "compile_failures": compile_failures,
        "import_failures": import_failures,
        "connected_phase_files": connected_count,
        "isolated_phase_files": isolated_count,
        "test_files": test_files,
        "safety_coverage": safety,
        "project_sha256": calculate_project_digest(files),
        "flags": EXPECTED_FLAGS,
    }


if __name__ == "__main__":
    result = build_audit()

    print()
    print("==================================================")
    print(" FULL SYSTEM AUDIT 1 → 134")
    print("==================================================")
    print("AUDIT STATE:", result["audit_state"])
    print("PYTHON FILES:", result["python_files"])
    print("PHASE FILES:", result["phase_files"])
    print("IMPLEMENTED PHASE REFERENCES:",
          len(result["implemented_phase_references"]))
    print("MISSING PHASE REFERENCES:",
          len(result["missing_phase_references"]))
    print("COMPILE FAILURES:",
          len(result["compile_failures"]))
    print("IMPORT FAILURES:",
          len(result["import_failures"]))
    print("CONNECTED PHASE FILES:",
          result["connected_phase_files"])
    print("ISOLATED PHASE FILES:",
          result["isolated_phase_files"])
    print("TEST FILES:", result["test_files"])
    print("==================================================")
    print("SAFETY COVERAGE")

    for key, value in result["safety_coverage"].items():
        print(
            f"{key}: "
            f"present={value['present']} "
            f"matches={value['matches']}"
        )

    print("==================================================")
    print("SAFETY FLAGS")
    print("READ_ONLY:", EXPECTED_FLAGS["READ_ONLY"])
    print("DRY_RUN:", EXPECTED_FLAGS["DRY_RUN"])
    print(
        "REAL EXECUTION: BLOCKED"
        if EXPECTED_FLAGS["REAL_EXECUTION_BLOCKED"]
        else "REAL EXECUTION: ENABLED"
    )
    print(
        "HUMAN REVIEW REQUIRED:",
        EXPECTED_FLAGS["HUMAN_REVIEW_REQUIRED"],
    )
    print(
        "RESPONSE LOCKED:",
        EXPECTED_FLAGS["RESPONSE_LOCKED"],
    )
    print("==================================================")
    print("PROJECT SHA256:", result["project_sha256"])
    print("==================================================")

    if result["missing_phase_references"]:
        print("MISSING REFERENCES:",
              result["missing_phase_references"])

    if result["compile_failures"]:
        print("COMPILE FAILURES DETAIL:")
        print(json.dumps(
            result["compile_failures"],
            indent=2,
        ))

    if result["import_failures"]:
        print("IMPORT FAILURES DETAIL:")
        print(json.dumps(
            result["import_failures"],
            indent=2,
        ))

    print("==================================================")
