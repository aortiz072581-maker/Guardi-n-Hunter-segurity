"""
Guardian Hunter — Connectivity Audit v3

Defensive architecture audit.

Measures:
- Python/phase inventory.
- Internal dependency graph.
- Incoming + outgoing connectivity.
- Explicit functional phase mappings.
- Phase 18 import integrity.
- Active pytest environment.
- Effective safety controls from runtime modules.

This audit does not execute response actions.
"""

from __future__ import annotations

import ast
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "guardian_hunter"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SAFETY_NAMES = (
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "RESPONSE_LOCKED",
)


# Functional implementations whose filenames do not carry
# the corresponding phase number.
#
# These mappings are based on the project's own phase tests.
FUNCTIONAL_PHASE_MAP = {
    23: [
        "guardian_hunter.correlation.advanced",
    ],
    24: [
        "guardian_hunter.evidence.incident",
    ],
    27: [
        "guardian_hunter.health.monitor",
    ],
    30: [
        "guardian_hunter.dashboard.phase28",
        "guardian_hunter.reports.phase29",
    ],
    44: [
        "guardian_hunter.risk_analytics.engine",
    ],
    45: [
        "guardian_hunter.readiness.assessment",
    ],
}


def all_python_files():
    return sorted(PACKAGE.rglob("*.py"))


def is_test_path(path):
    """Return True for Python test modules excluded from architecture metrics."""
    rel = path.relative_to(ROOT)

    return (
        "tests" in rel.parts
        or path.name.startswith("test_")
    )


def implementation_python_files():
    """Production Python files only; tests are validation, not architecture."""
    return [
        p
        for p in all_python_files()
        if not is_test_path(p)
    ]


def phase_files():
    """Production implementation modules whose filename declares a phase."""
    return [
        p
        for p in implementation_python_files()
        if "phase" in p.name.lower()
    ]


def path_to_module(path):
    rel = path.relative_to(ROOT)

    if path.name == "__init__.py":
        return ".".join(rel.parent.parts)

    return ".".join(
        rel.with_suffix("").parts
    )


def module_exists(module_name):
    parts = module_name.split(".")

    py_file = ROOT.joinpath(*parts).with_suffix(".py")
    package_file = ROOT.joinpath(*parts) / "__init__.py"

    return py_file.exists() or package_file.exists()


def resolve_relative_import(current_module, level, module):
    parts = current_module.split(".")

    # A normal module's final component is the filename.
    package_parts = parts[:-1]

    if level > len(package_parts) + 1:
        return None

    keep = len(package_parts) - level + 1

    if keep < 0:
        return None

    base = package_parts[:keep]

    if module:
        base += module.split(".")

    if not base:
        return None

    return ".".join(base)


def inspect_imports(path):
    module_name = path_to_module(path)

    imports = []
    guardian_imports = []

    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            ),
            filename=str(path),
        )

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

                    if (
                        alias.name == "guardian_hunter"
                        or alias.name.startswith(
                            "guardian_hunter."
                        )
                    ):
                        guardian_imports.append(
                            alias.name
                        )

            elif isinstance(node, ast.ImportFrom):
                target = None

                if node.level:
                    target = resolve_relative_import(
                        module_name,
                        node.level,
                        node.module,
                    )
                elif node.module:
                    target = node.module

                if target:
                    imports.append(target)

                    if (
                        target == "guardian_hunter"
                        or target.startswith(
                            "guardian_hunter."
                        )
                    ):
                        guardian_imports.append(
                            target
                        )

    except Exception as exc:
        return {
            "file": str(path),
            "module": module_name,
            "imports": [],
            "guardian_imports": [],
            "parse_error": repr(exc),
        }

    guardian_imports = sorted(
        set(guardian_imports)
    )

    return {
        "file": str(path),
        "module": module_name,
        "imports": imports,
        "guardian_imports": guardian_imports,
    }


def build_dependency_graph(files):
    inspected = [
        inspect_imports(path)
        for path in files
    ]

    module_names = {
        item["module"]
        for item in inspected
    }

    incoming = {
        module: set()
        for module in module_names
    }

    outgoing = {
        module: set()
        for module in module_names
    }

    def match_project_module(target):
        if target in module_names:
            return target

        candidates = [
            module
            for module in module_names
            if target.startswith(
                module + "."
            )
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=len,
        )

    for item in inspected:
        source = item["module"]

        for target in item.get(
            "guardian_imports",
            [],
        ):
            matched = match_project_module(
                target
            )

            if not matched:
                continue

            if matched == source:
                continue

            outgoing[source].add(matched)
            incoming[matched].add(source)

    records = []

    for item in inspected:
        module = item["module"]

        inc = sorted(incoming[module])
        out = sorted(outgoing[module])

        records.append({
            **item,
            "incoming": inc,
            "outgoing": out,
            "incoming_count": len(inc),
            "outgoing_count": len(out),
            "connected": bool(inc or out),
        })

    return records


def run_pytest():
    command = [
        sys.executable,
        "-m",
        "pytest",
        "guardian_hunter/tests",
        "tests",
        "-q",
        "--disable-warnings",
    ]

    env = os.environ.copy()

    existing = env.get(
        "PYTHONPATH",
        "",
    )

    env["PYTHONPATH"] = (
        str(ROOT)
        if not existing
        else str(ROOT)
        + os.pathsep
        + existing
    )

    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
        )

        return {
            "executed": True,
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
        }

    except Exception as exc:
        return {
            "executed": False,
            "reason": repr(exc),
        }


def import_module(module_name):
    try:
        importlib.import_module(
            module_name
        )

        return {
            "module": module_name,
            "ok": True,
        }

    except Exception as exc:
        return {
            "module": module_name,
            "ok": False,
            "error": repr(exc),
        }


def phase18_audit():
    candidates = []

    for path in all_python_files():
        if "phase18" in path.name.lower():
            candidates.append(path)

    results = []

    for path in candidates:
        module = path_to_module(path)

        results.append({
            "file": str(path),
            "module": module,
            "import": import_module(
                module
            ),
        })

    return results


def filename_phase_numbers(path):
    """
    Extract only explicit phase numbers from filenames.

    Examples:
      phase21.py -> 21
      phase21_orchestrator.py -> 21
      test_phase22_24.py -> 22,24

    Functional mappings are added separately.
    """

    name = path.stem.lower()

    numbers = set()

    for match in re.finditer(
        r"phase(?:s)?[_-]?(\d+)",
        name,
    ):
        numbers.add(
            int(match.group(1))
        )

    # Handle ranges such as:
    # test_phase22_24
    range_match = re.search(
        r"phase(?:s)?[_-]?(\d+)[_-](\d+)",
        name,
    )

    if range_match:
        start = int(
            range_match.group(1)
        )
        end = int(
            range_match.group(2)
        )

        if start <= end:
            numbers.update(
                range(start, end + 1)
            )

    return numbers


def phase_coverage():
    """
    Map production phase implementations.

    Coverage bounds are derived from implementation filenames and explicit
    functional mappings instead of a hardcoded historical 1..134 range.
    """
    implementation_files = implementation_python_files()

    declared_numbers = set(
        FUNCTIONAL_PHASE_MAP
    )

    for path in implementation_files:
        declared_numbers.update(
            filename_phase_numbers(path)
        )

    if not declared_numbers:
        return {}

    first_phase = min(declared_numbers)
    last_phase = max(declared_numbers)

    coverage = {
        number: set()
        for number in range(
            first_phase,
            last_phase + 1,
        )
    }

    # Filename-based production mappings.
    for path in implementation_files:
        for number in filename_phase_numbers(
            path
        ):
            if number in coverage:
                coverage[number].add(
                    str(path)
                )

    # Explicit functional mappings.
    for number, modules in (
        FUNCTIONAL_PHASE_MAP.items()
    ):
        for module in modules:
            if not module_exists(module):
                continue

            parts = module.split(".")

            module_file = (
                ROOT.joinpath(*parts)
                .with_suffix(".py")
            )

            package_file = (
                ROOT.joinpath(*parts)
                / "__init__.py"
            )

            target = (
                module_file
                if module_file.exists()
                else package_file
            )

            coverage[number].add(
                str(target)
            )

    return {
        number: sorted(files)
        for number, files
        in coverage.items()
    }


def safety_audit():
    """
    Validate the effective five-lock contract against
    independent runtime modules that implement it.

    No value is hardcoded as PASS.
    """

    sources = (
        "guardian_hunter.evidence.persistence",
        "guardian_hunter.incident.state",
    )

    source_results = {}

    for module_name in sources:
        try:
            module = importlib.import_module(
                module_name
            )

            values = {
                name: getattr(
                    module,
                    name,
                    None,
                )
                for name in SAFETY_NAMES
            }

            source_results[module_name] = {
                "import_ok": True,
                "values": values,
                "all_locked": all(
                    value is True
                    for value in values.values()
                ),
            }

        except Exception as exc:
            source_results[module_name] = {
                "import_ok": False,
                "error": repr(exc),
                "values": {
                    name: None
                    for name in SAFETY_NAMES
                },
                "all_locked": False,
            }

    effective = {}

    for name in SAFETY_NAMES:
        observed = [
            item.get(
                "values",
                {},
            ).get(name)
            for item in source_results.values()
        ]

        effective[name] = (
            bool(observed)
            and all(
                value is True
                for value in observed
            )
        )

    verified = all(
        effective.values()
    )

    return {
        **effective,
        "verified": verified,
        "sources": source_results,
    }


def main():
    files = all_python_files()
    phases = phase_files()

    graph = build_dependency_graph(
        phases
    )

    connected = [
        item
        for item in graph
        if item.get("connected")
    ]

    isolated = [
        item
        for item in graph
        if not item.get("connected")
    ]

    coverage = phase_coverage()

    missing = [
        number
        for number, mappings
        in coverage.items()
        if not mappings
    ]

    phase18 = phase18_audit()
    pytest_result = run_pytest()
    safety = safety_audit()

    print()
    print(
        "=================================================="
    )
    print(
        " CONNECTIVITY AUDIT v3"
    )
    print(
        "=================================================="
    )

    print(
        "PYTHON FILES:",
        len(files),
    )
    print(
        "PHASE FILES:",
        len(phases),
    )
    print(
        "CONNECTED:",
        len(connected),
    )
    print(
        "ISOLATED:",
        len(isolated),
    )
    print(
        "MISSING FILE MAPPINGS:",
        len(missing),
    )

    print(
        "=================================================="
    )
    print("PHASE COVERAGE")
    print(
        "--------------------------------------------------"
    )

    for number in sorted(coverage):
        mappings = coverage[number]

        if mappings:
            print(
                f"PHASE {number:03d}: "
                f"{len(mappings)} FILE(S)"
            )
        else:
            print(
                f"PHASE {number:03d}: "
                "NO FILE MAPPING"
            )

    print(
        "=================================================="
    )
    print(
        "PHASE 18 DIRECT IMPORT AUDIT"
    )
    print(
        "=================================================="
    )

    failures18 = []

    for item in phase18:
        if not item["import"]["ok"]:
            failures18.append(item)
            print(item)

    print(
        "PHASE18 CHECKED:",
        len(phase18),
    )
    print(
        "PHASE18 FAILURES:",
        len(failures18),
    )

    print(
        "=================================================="
    )
    print("PYTEST REAL ENVIRONMENT")
    print(
        "=================================================="
    )

    print(
        "PYTEST EXIT:",
        pytest_result.get(
            "returncode"
        ),
    )

    print(
        "=================================================="
    )
    print("SAFETY MODE — VERIFIED")
    print(
        "=================================================="
    )

    for name in SAFETY_NAMES:
        print(
            f"{name}: "
            f"{safety[name]}"
        )

    print(
        "SAFETY VERIFIED:",
        safety["verified"],
    )

    print(
        "=================================================="
    )
    print("ISOLATED SAMPLE")
    print(
        "=================================================="
    )

    for item in isolated[:40]:
        print(item["module"])

    report = {
        "audit_version": 3,
        "python_files": len(files),
        "phase_files": len(phases),
        "connected": len(connected),
        "isolated": len(isolated),
        "missing_file_mappings": missing,
        "phase_coverage": coverage,
        "functional_phase_map": (
            FUNCTIONAL_PHASE_MAP
        ),
        "phase18": phase18,
        "pytest": pytest_result,
        "safety": safety,
        "connectivity": graph,
        "isolated_modules": [
            item["module"]
            for item in isolated
        ],
    }

    output = (
        PACKAGE
        / "audit"
        / "connectivity_audit_v2.json"
    )

    output.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "REPORT:",
        output,
    )

    failures = []

    if failures18:
        failures.append(
            "PHASE18_IMPORT_FAILURES"
        )

    if pytest_result.get(
        "returncode"
    ) != 0:
        failures.append(
            "PYTEST_FAILURE"
        )

    if not safety["verified"]:
        failures.append(
            "SAFETY_NOT_VERIFIED"
        )

    print(
        "=================================================="
    )

    if failures:
        print(
            "AUDIT RESULT: FAIL"
        )
        print(
            "FAILURES:",
            ", ".join(failures),
        )
        raise SystemExit(1)

    print(
        "AUDIT RESULT: PASS"
    )
    print(
        "CONNECTIVITY AUDIT v3 — FIN"
    )
    print(
        "=================================================="
    )


if __name__ == "__main__":
    main()
