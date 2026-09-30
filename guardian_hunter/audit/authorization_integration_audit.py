"""
Guardian Hunter — Authorization → Decision/Response Integration Audit

Purpose:
- Audit the integration surface between authorization, decision and response.
- READ_ONLY=True
- DRY_RUN=True
- REAL_EXECUTION_BLOCKED=True
- HUMAN_REVIEW_REQUIRED=True
- RESPONSE_LOCKED=True

This module is audit-only.
It does not execute response actions.
It does not modify Phase 18.
It does not authorize real execution.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


ROOT = Path(__file__).resolve().parents[2]

TARGETS = (
    "guardian_hunter.authorization.contract",
    "guardian_hunter.authorization.phase18_bridge",
    "guardian_hunter.decision.engine",
    "guardian_hunter.response.policy",
    "guardian_hunter.response.orchestrator",
)


@dataclass(frozen=True)
class ModuleAudit:
    module: str
    import_ok: bool
    functions: tuple[str, ...]
    classes: tuple[str, ...]
    authorized_parameters: tuple[str, ...]
    execution_allowed_true: int
    execution_allowed_false: int
    forbidden_calls: tuple[str, ...]
    authorization_references: tuple[str, ...]


FORBIDDEN_CALL_NAMES = {
    "exec",
    "eval",
    "system",
    "popen",
    "Popen",
    "call",
    "check_call",
    "check_output",
}


def _module_path(module_name: str) -> Path:
    return ROOT / Path(module_name.replace(".", "/")).with_suffix(".py")


def _call_name(node: ast.Call) -> str:
    fn = node.func

    if isinstance(fn, ast.Name):
        return fn.id

    if isinstance(fn, ast.Attribute):
        return fn.attr

    return ""


def _source_checks(
    module_name: str,
    source: str,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    int,
    int,
    tuple[str, ...],
    tuple[str, ...],
]:
    tree = ast.parse(source, filename=module_name)

    functions: list[str] = []
    classes: list[str] = []
    authorized_parameters: list[str] = []
    forbidden: list[str] = []
    authorization_refs: list[str] = []

    execution_allowed_true = 0
    execution_allowed_false = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

            for arg in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            ):
                if arg.arg in {
                    "authorized",
                    "authorization",
                    "authorization_id",
                    "authorization_request",
                    "auth",
                }:
                    authorized_parameters.append(
                        f"{node.name}({arg.arg})"
                    )

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Call):
            name = _call_name(node)

            if name in FORBIDDEN_CALL_NAMES:
                forbidden.append(
                    f"{name}@line{getattr(node, 'lineno', '?')}"
                )

            for kw in node.keywords:
                if kw.arg == "shell":
                    if isinstance(kw.value, ast.Constant):
                        if kw.value.value is True:
                            forbidden.append(
                                f"shell=True@line{getattr(node, 'lineno', '?')}"
                            )

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "execution_allowed":
                        if isinstance(node.value, ast.Constant):
                            if node.value.value is True:
                                execution_allowed_true += 1
                            elif node.value.value is False:
                                execution_allowed_false += 1

        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                if node.target.id == "execution_allowed":
                    if isinstance(node.value, ast.Constant):
                        if node.value.value is True:
                            execution_allowed_true += 1
                        elif node.value.value is False:
                            execution_allowed_false += 1

    lowered = source.lower()

    markers = (
        "authorizationengine",
        "authorizationrequest",
        "authorizationdecision",
        "authorization_contract",
        "phase18_bridge",
        "human_review_required",
        "response_locked",
        "real_execution_blocked",
    )

    for marker in markers:
        if marker in lowered:
            authorization_refs.append(marker)

    return (
        tuple(sorted(set(functions))),
        tuple(sorted(set(classes))),
        execution_allowed_true,
        execution_allowed_false,
        tuple(sorted(set(forbidden))),
        tuple(sorted(set(authorization_refs))),
    )


def audit_module(module_name: str) -> ModuleAudit:
    path = _module_path(module_name)

    if not path.exists():
        return ModuleAudit(
            module=module_name,
            import_ok=False,
            functions=(),
            classes=(),
            authorized_parameters=(),
            execution_allowed_true=0,
            execution_allowed_false=0,
            forbidden_calls=(f"FILE_MISSING:{path}",),
            authorization_references=(),
        )

    try:
        importlib.import_module(module_name)
        import_ok = True
    except Exception:
        import_ok = False

    source = path.read_text(encoding="utf-8")

    (
        functions,
        classes,
        execution_allowed_true,
        execution_allowed_false,
        forbidden_calls,
        authorization_references,
    ) = _source_checks(module_name, source)

    return ModuleAudit(
        module=module_name,
        import_ok=import_ok,
        functions=functions,
        classes=classes,
        authorized_parameters=authorized_parameters_from_source(source),
        execution_allowed_true=execution_allowed_true,
        execution_allowed_false=execution_allowed_false,
        forbidden_calls=forbidden_calls,
        authorization_references=authorization_references,
    )


def authorized_parameters_from_source(source: str) -> tuple[str, ...]:
    tree = ast.parse(source)

    found: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            ):
                if arg.arg in {
                    "authorized",
                    "authorization",
                    "authorization_id",
                    "authorization_request",
                    "auth",
                }:
                    found.append(f"{node.name}({arg.arg})")

    return tuple(sorted(set(found)))


def audit_contract_runtime() -> tuple[bool, str]:
    try:
        contract = importlib.import_module(
            "guardian_hunter.authorization.contract"
        )

        required = (
            "AuthorizationEngine",
            "AuthorizationRequest",
            "Identity",
            "Role",
            "Permission",
            "AuthorizationState",
        )

        missing = [
            name for name in required
            if not hasattr(contract, name)
        ]

        if missing:
            return False, f"MISSING_CONTRACT_SYMBOLS:{missing}"

        engine = contract.AuthorizationEngine()

        identity = contract.Identity(
            actor_id="audit-actor",
            role=contract.Role.ADMIN,
            active=True,
        )

        now = __import__("time").time()

        request = contract.AuthorizationRequest(
            request_id="audit-request",
            authorization_id="audit-auth",
            actor_id="audit-actor",
            action="request_response",
            nonce="audit-nonce",
            issued_at=now - 1,
            expires_at=now + 60,
            requires_human_review=True,
        )

        decision = engine.authorize(identity, request)

        if getattr(decision, "execution_allowed", False) is not False:
            return False, "EXECUTION_ALLOWED_NOT_FALSE"

        return True, "CONTRACT_RUNTIME_OK"

    except Exception as exc:
        return False, f"CONTRACT_RUNTIME_ERROR:{type(exc).__name__}:{exc}"


def audit_decision_runtime() -> tuple[bool, str]:
    try:
        module = importlib.import_module(
            "guardian_hunter.decision.engine"
        )

        if not hasattr(module, "Decision"):
            return False, "DECISION_CLASS_MISSING"

        decision_cls = module.Decision

        fields = getattr(decision_cls, "__dataclass_fields__", {})

        if "execution_allowed" not in fields:
            return False, "DECISION_EXECUTION_FIELD_MISSING"

        return True, "DECISION_INTERFACE_OK"

    except Exception as exc:
        return False, f"DECISION_RUNTIME_ERROR:{type(exc).__name__}:{exc}"


def audit_response_interfaces() -> tuple[bool, str]:
    checks = {
        "guardian_hunter.response.policy": (
            "classify_response",
            "build_policy_decision",
        ),
        "guardian_hunter.response.orchestrator": (
            "create_incident",
        ),
    }

    missing: list[str] = []

    for module_name, symbols in checks.items():
        try:
            module = importlib.import_module(module_name)

            for symbol in symbols:
                if not hasattr(module, symbol):
                    missing.append(f"{module_name}:{symbol}")

        except Exception as exc:
            missing.append(
                f"{module_name}:IMPORT:{type(exc).__name__}"
            )

    if missing:
        return False, f"MISSING_RESPONSE_INTERFACE:{missing}"

    return True, "RESPONSE_INTERFACES_OK"


def audit_integration_surface(results: list[ModuleAudit]) -> tuple[bool, str]:
    target_map = {item.module: item for item in results}

    decision = target_map.get("guardian_hunter.decision.engine")
    policy = target_map.get("guardian_hunter.response.policy")
    orchestrator = target_map.get(
        "guardian_hunter.response.orchestrator"
    )

    if not decision or not policy or not orchestrator:
        return False, "INTEGRATION_TARGET_MISSING"

    response_authorized = (
        len(policy.authorized_parameters) > 0
        and len(orchestrator.authorized_parameters) > 0
    )

    if not response_authorized:
        return False, "AUTHORIZED_RESPONSE_SURFACE_MISSING"

    return True, "INTEGRATION_SURFACE_PRESENT"


def audit_safety(results: list[ModuleAudit]) -> tuple[bool, str]:
    if not READ_ONLY:
        return False, "READ_ONLY_FALSE"

    if not DRY_RUN:
        return False, "DRY_RUN_FALSE"

    if not REAL_EXECUTION_BLOCKED:
        return False, "REAL_EXECUTION_BLOCKED_FALSE"

    if not HUMAN_REVIEW_REQUIRED:
        return False, "HUMAN_REVIEW_REQUIRED_FALSE"

    if not RESPONSE_LOCKED:
        return False, "RESPONSE_LOCKED_FALSE"

    for item in results:
        if item.execution_allowed_true > 0:
            return False, (
                f"EXECUTION_ALLOWED_TRUE:{item.module}:"
                f"{item.execution_allowed_true}"
            )

        if item.forbidden_calls:
            return False, (
                f"FORBIDDEN_EXECUTION:{item.module}:"
                f"{item.forbidden_calls}"
            )

    return True, "SAFETY_INVARIANTS_OK"


def main() -> int:
    print("=" * 70)
    print("GUARDIAN HUNTER — AUTHORIZATION INTEGRATION AUDIT")
    print("=" * 70)

    results: list[ModuleAudit] = []

    for module_name in TARGETS:
        result = audit_module(module_name)
        results.append(result)

        print()
        print(f"[MODULE] {module_name}")
        print(f"  IMPORT: {'OK' if result.import_ok else 'FAIL'}")
        print(f"  FUNCTIONS: {len(result.functions)}")
        print(f"  CLASSES: {len(result.classes)}")
        print(
            "  AUTHORIZED PARAMETERS:",
            len(result.authorized_parameters),
        )
        print(
            "  EXECUTION_ALLOWED=True:",
            result.execution_allowed_true,
        )
        print(
            "  EXECUTION_ALLOWED=False:",
            result.execution_allowed_false,
        )
        print(
            "  FORBIDDEN EXECUTION:",
            len(result.forbidden_calls),
        )
        print(
            "  AUTH REFERENCES:",
            ", ".join(result.authorization_references)
            if result.authorization_references
            else "NONE",
        )

    checks = []

    contract_ok, contract_msg = audit_contract_runtime()
    checks.append(contract_ok)
    print()
    print("CONTRACT RUNTIME:", contract_msg)

    decision_ok, decision_msg = audit_decision_runtime()
    checks.append(decision_ok)
    print("DECISION INTERFACE:", decision_msg)

    response_ok, response_msg = audit_response_interfaces()
    checks.append(response_ok)
    print("RESPONSE INTERFACES:", response_msg)

    integration_ok, integration_msg = audit_integration_surface(results)
    checks.append(integration_ok)
    print("INTEGRATION SURFACE:", integration_msg)

    safety_ok, safety_msg = audit_safety(results)
    checks.append(safety_ok)
    print("SAFETY:", safety_msg)

    all_imports_ok = all(item.import_ok for item in results)
    checks.append(all_imports_ok)

    print()
    print("=" * 70)

    if all(checks):
        print("AUDIT STATE: AUTHORIZATION_INTEGRATION_AUDIT_OK")
    else:
        print("AUDIT STATE: AUTHORIZATION_INTEGRATION_REVIEW_REQUIRED")

    print()
    print("READ_ONLY:", READ_ONLY)
    print("DRY_RUN:", DRY_RUN)
    print("REAL_EXECUTION_BLOCKED:", REAL_EXECUTION_BLOCKED)
    print("HUMAN_REVIEW_REQUIRED:", HUMAN_REVIEW_REQUIRED)
    print("RESPONSE_LOCKED:", RESPONSE_LOCKED)
    print("REAL EXECUTION: BLOCKED")
    print("=" * 70)

    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
