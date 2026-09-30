from __future__ import annotations

import ast
import importlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "guardian_hunter"
REPORT = PKG / "audit" / "connectivity_audit_v5.json"

SAFETY_NAMES = (
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "RESPONSE_LOCKED",
)

SEMANTIC_PHASES = {
    23: ("guardian_hunter.correlation.advanced",),
    24: ("guardian_hunter.evidence.incident",),
    27: ("guardian_hunter.health.monitor",),
    30: ("guardian_hunter.dashboard.phase28", "guardian_hunter.reports.phase29"),
    43: ("guardian_hunter.cases.manager",),
    44: ("guardian_hunter.risk_analytics.engine",),
    45: ("guardian_hunter.readiness.assessment",),
    135: ("guardian_hunter.omniroute.phase135_138_preflight",),
    136: ("guardian_hunter.omniroute.phase135_138_preflight",),
    137: ("guardian_hunter.omniroute.phase135_138_preflight",),
    138: ("guardian_hunter.omniroute.phase135_138_preflight",),
    139: ("guardian_hunter.runtime.node_runtime",),
    140: ("guardian_hunter.runtime.node_runtime",),
    141: ("guardian_hunter.runtime.node_runtime",),
    142: ("guardian_hunter.product.demo",),
    143: ("guardian_hunter.product.api_contract",),
    145: ("guardian_hunter.product.metrics",),
    150: ("guardian_hunter.product.readiness",),
    151: ("guardian_hunter.release.release_manifest",),
    152: ("guardian_hunter.due_diligence.dependency_inventory",),
    153: ("guardian_hunter.release.test_evidence",),
    159: ("guardian_hunter.release.release_readiness",),
    160: ("guardian_hunter.product.buyer_readiness",),
}

UNMAPPED_LOGICAL_MILESTONES = (144, 146, 147, 148, 149, 154, 155, 156, 157, 158)

def productive_files():
    result = []
    for p in PKG.rglob("*.py"):
        s = str(p)
        if "tests" in p.parts:
            continue
        if "__pycache__" in s or ".bak_" in p.name:
            continue
        result.append(p)
    return sorted(result)

def module_name(path):
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)

def resolve_from(current, node, modules=None):
    if node.level == 0:
        return node.module or ""

    parts = current.split(".")

    # If current is a package (__init__.py), relative imports
    # resolve from the package itself. Otherwise they resolve
    # from the containing package.
    if modules is not None:
        path = modules.get(current)
        is_package = bool(
            path is not None
            and path.name == "__init__.py"
        )
    else:
        is_package = False

    package = parts if is_package else parts[:-1]

    up = node.level - 1

    if up:
        package = (
            package[:-up]
            if up <= len(package)
            else []
        )

    if node.module:
        package += node.module.split(".")

    return ".".join(package)

def graph(files):
    modules = {module_name(p): p for p in files}
    outgoing = defaultdict(set)
    incoming = defaultdict(set)

    for mod, path in modules.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = resolve_from(
                    mod,
                    node,
                    modules,
                )
                if base:
                    names.append(base)
                for alias in node.names:
                    if alias.name != "*" and base:
                        names.append(base + "." + alias.name)

            for name in names:
                candidate = name
                while candidate:
                    if candidate in modules and candidate != mod:
                        outgoing[mod].add(candidate)
                        incoming[candidate].add(mod)
                        break
                    if "." not in candidate:
                        break
                    candidate = candidate.rsplit(".", 1)[0]

    return modules, outgoing, incoming

def physical_phases(modules):
    result = defaultdict(set)
    rx = re.compile(r"phase(\d{2,3})(?:_(\d{2,3}))?", re.I)
    for mod in modules:
        leaf = mod.rsplit(".", 1)[-1]
        m = rx.search(leaf)
        if not m:
            continue
        start = int(m.group(1))
        end = int(m.group(2) or start)
        if end < start or end - start > 50:
            continue
        for n in range(start, end + 1):
            result[n].add(mod)
    return result

def test_imports():
    refs = set()
    for p in PKG.rglob("test*.py"):
        if ".bak_" in p.name:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                refs.update(a.name for a in node.names if a.name.startswith("guardian_hunter"))
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("guardian_hunter"):
                refs.add(node.module)
    return refs

def safety():
    sources = (
        "guardian_hunter.evidence.persistence",
        "guardian_hunter.incident.state",
    )
    values = {}
    ok = True
    for src in sources:
        mod = importlib.import_module(src)
        values[src] = {}
        for name in SAFETY_NAMES:
            value = getattr(mod, name, None)
            values[src][name] = value
            ok = ok and value is True
    return ok, values

def main():
    files = productive_files()
    modules, outgoing, incoming = graph(files)
    physical = physical_phases(modules)
    tested_raw = test_imports()

    tested = set()
    for ref in tested_raw:
        candidate = ref
        while candidate:
            if candidate in modules:
                tested.add(candidate)
                break
            if "." not in candidate:
                break
            candidate = candidate.rsplit(".", 1)[0]

    runtime_connected = {
        m for m in modules
        if outgoing.get(m) or incoming.get(m)
    }

    contract_tested = set(tested) & set(modules)
    uncovered = set(modules) - runtime_connected - contract_tested

    package_initializers = {
        m
        for m in uncovered
        if modules[m].name == "__init__.py"
    }

    standalone_tools = set()

    for m in uncovered - package_initializers:
        path = modules[m]

        try:
            tree = ast.parse(
                path.read_text(encoding="utf-8")
            )
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in tree.body:
            if not isinstance(node, ast.If):
                continue

            try:
                condition = ast.unparse(node.test)
            except Exception:
                condition = ""

            if (
                "__name__" in condition
                and "__main__" in condition
            ):
                standalone_tools.add(m)
                break

    regular_orphan_candidates = (
        uncovered
        - package_initializers
        - standalone_tools
    )

    logical = defaultdict(set)
    source_kind = defaultdict(set)

    for phase, mods in physical.items():
        logical[phase].update(mods)
        source_kind[phase].add("physical")

    for phase, mods in SEMANTIC_PHASES.items():
        for mod in mods:
            if mod in modules:
                logical[phase].add(mod)
                source_kind[phase].add("semantic")

    safety_ok, safety_values = safety()

    data = {
        "audit_version": 5,
        "productive_python_files": len(files),
        "runtime_connected": len(runtime_connected),
        "contract_tested": len(contract_tested),
        "runtime_or_contract": len(runtime_connected | contract_tested),
        "uncovered_modules": len(uncovered),
        "package_initializers": len(package_initializers),
        "standalone_tools": len(standalone_tools),
        "regular_orphan_candidates": len(regular_orphan_candidates),
        "orphan_candidates": len(regular_orphan_candidates),
        "physical_phase_numbers": sorted(physical),
        "semantic_phase_numbers": sorted(SEMANTIC_PHASES),
        "logical_phase_numbers": sorted(logical),
        "unmapped_logical_milestones": list(UNMAPPED_LOGICAL_MILESTONES),
        "safety_verified": safety_ok,
        "safety": safety_values,
        "runtime_connected_modules": sorted(runtime_connected),
        "contract_tested_modules": sorted(contract_tested),
        "uncovered_module_names": sorted(uncovered),
        "package_initializer_modules": sorted(package_initializers),
        "standalone_tool_modules": sorted(standalone_tools),
        "regular_orphan_candidate_modules": sorted(regular_orphan_candidates),
        "orphan_candidate_modules": sorted(regular_orphan_candidates),
        "logical_phase_map": {
            str(n): {
                "modules": sorted(logical[n]),
                "source_kind": sorted(source_kind[n]),
            }
            for n in sorted(logical)
        },
    }

    REPORT.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    print("=" * 60)
    print(" CONNECTIVITY AUDIT v5 — SEMANTIC/PRODUCTIVE")
    print("=" * 60)
    print("PRODUCTIVE PYTHON FILES:", len(files))
    print("RUNTIME CONNECTED:", len(runtime_connected))
    print("CONTRACT TESTED:", len(contract_tested))
    print("RUNTIME OR CONTRACT:", len(runtime_connected | contract_tested))
    print("UNCOVERED MODULES:", len(uncovered))
    print("PACKAGE INITIALIZERS:", len(package_initializers))
    print("STANDALONE TOOLS:", len(standalone_tools))
    print("REGULAR ORPHAN CANDIDATES:", len(regular_orphan_candidates))
    print("PHYSICAL PHASE NUMBERS:", len(physical))
    print("SEMANTIC PHASE NUMBERS:", len(SEMANTIC_PHASES))
    print("LOGICAL PHASE NUMBERS:", len(logical))
    print("UNMAPPED MILESTONES:", list(UNMAPPED_LOGICAL_MILESTONES))
    print("SAFETY VERIFIED:", safety_ok)
    print()
    print("E2E RUNTIME CONNECTIONS:")
    for m in sorted(runtime_connected):
        if m.startswith("guardian_hunter.integration") or m in {
            "guardian_hunter.pipeline.engine",
            "guardian_hunter.modules.hunter",
            "guardian_hunter.decision.engine",
            "guardian_hunter.evidence.persistence",
            "guardian_hunter.authorization.decision_response_adapter",
        }:
            print(" ", m)
    print()
    print("ORPHAN SAMPLE:")
    for m in sorted(regular_orphan_candidates)[:50]:
        print(" ", m)
    print()
    print("REPORT:", REPORT)
    print("AUDIT RESULT:", "PASS" if safety_ok else "FAIL")
    return 0 if safety_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
