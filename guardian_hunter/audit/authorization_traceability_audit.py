"""
Guardian Hunter — Authorization Traceability Audit v1

Scope:
    Identity -> Role -> Permission -> Request -> Decision
    -> Anti-Replay -> Audit Chain -> Decision/Response
    -> Fail-Closed -> Real Execution Blocked

This module is AUDIT ONLY.

It does not:
- modify Phase 18
- authorize real execution
- execute responses
- change the authorization contract
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import time
from pathlib import Path

from guardian_hunter.authorization.contract import (
    AuthorizationEngine,
    AuthorizationRequest,
    AuthorizationState,
    Identity,
    Permission,
    Role,
)
from guardian_hunter.authorization.decision_response_adapter import (
    AuthorizationDecisionResponseAdapter,
)


ROOT = Path(__file__).resolve().parents[2]

SAFETY = {
    "READ_ONLY": True,
    "DRY_RUN": True,
    "REAL_EXECUTION_BLOCKED": True,
    "HUMAN_REVIEW_REQUIRED": True,
    "RESPONSE_LOCKED": True,
}


def _check_fail_closed() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="audit-observer",
        role=Role.OBSERVER,
        active=True,
    )

    request = AuthorizationRequest(
        request_id="audit-denied-request",
        authorization_id="audit-denied-auth",
        actor_id="audit-observer",
        action=Permission.REQUEST_RESPONSE,
        nonce="audit-denied-nonce",
        issued_at=time.time(),
        expires_at=time.time() + 300,
    )

    decision = engine.authorize(identity, request)

    ok = (
        decision.authorized is False
        and decision.state == AuthorizationState.DENIED
        and decision.execution_allowed is False
    )

    return ok, "OBSERVER cannot REQUEST_RESPONSE"


def _check_actor_binding() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="actor-A",
        role=Role.OPERATOR,
        active=True,
    )

    request = AuthorizationRequest(
        request_id="binding-request",
        authorization_id="binding-auth",
        actor_id="actor-B",
        action=Permission.REQUEST_RESPONSE,
        nonce="binding-nonce",
        issued_at=time.time(),
        expires_at=time.time() + 300,
    )

    decision = engine.authorize(identity, request)

    ok = (
        decision.authorized is False
        and decision.execution_allowed is False
    )

    return ok, "actor binding enforced"


def _check_replay() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-replay",
        role=Role.OPERATOR,
        active=True,
    )

    now = time.time()

    request = AuthorizationRequest(
        request_id="replay-request",
        authorization_id="replay-auth",
        actor_id="operator-replay",
        action=Permission.REQUEST_RESPONSE,
        nonce="replay-nonce",
        issued_at=now,
        expires_at=now + 300,
    )

    first = engine.authorize(identity, request)
    second = engine.authorize(identity, request)

    ok = (
        first.authorized is True
        and first.execution_allowed is False
        and second.authorized is False
        and second.state == AuthorizationState.REPLAYED
        and second.execution_allowed is False
    )

    return ok, "nonce replay rejected"


def _check_expiration() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="expired-operator",
        role=Role.OPERATOR,
        active=True,
    )

    now = time.time()

    request = AuthorizationRequest(
        request_id="expired-request",
        authorization_id="expired-auth",
        actor_id="expired-operator",
        action=Permission.REQUEST_RESPONSE,
        nonce="expired-nonce",
        issued_at=now - 300,
        expires_at=now - 1,
    )

    decision = engine.authorize(identity, request)

    ok = (
        decision.authorized is False
        and decision.state == AuthorizationState.EXPIRED
        and decision.execution_allowed is False
    )

    return ok, "expired authorization rejected"


def _check_permission_boundary() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="analyst-boundary",
        role=Role.ANALYST,
        active=True,
    )

    now = time.time()

    request = AuthorizationRequest(
        request_id="permission-boundary",
        authorization_id="permission-boundary-auth",
        actor_id="analyst-boundary",
        action=Permission.APPROVE_RESPONSE,
        nonce="permission-boundary-nonce",
        issued_at=now,
        expires_at=now + 300,
    )

    decision = engine.authorize(identity, request)

    ok = (
        decision.authorized is False
        and decision.execution_allowed is False
    )

    return ok, "role permission boundary enforced"


def _check_human_review() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    identity = Identity(
        actor_id="operator-review",
        role=Role.OPERATOR,
        active=True,
    )

    now = time.time()

    request = AuthorizationRequest(
        request_id="human-review",
        authorization_id="human-review-auth",
        actor_id="operator-review",
        action=Permission.REQUEST_RESPONSE,
        nonce="human-review-nonce",
        issued_at=now,
        expires_at=now + 300,
        requires_human_review=False,
    )

    decision = engine.authorize(identity, request)

    ok = (
        decision.authorized is False
        and decision.execution_allowed is False
    )

    return ok, "human review remains mandatory"


def _check_adapter_path() -> tuple[bool, str]:
    adapter = AuthorizationDecisionResponseAdapter()

    result = adapter.authorize_and_prepare_response(
        actor_id="trace-operator",
        role="OPERATOR",
        action="request_response",
        request_id="trace-request",
        authorization_id="trace-auth",
        nonce="trace-adapter-nonce",
        risk_level="MEDIUM",
        reason="authorization traceability audit",
        target="audit-target",
        risk_data={"audit": True},
        issued_at=time.time(),
        expires_at=time.time() + 300,
    )

    ok = (
        result.execution_allowed is False
        and result.real_execution_blocked is True
        and result.human_review_required is True
        and result.response_locked is True
        and result.read_only is True
        and result.dry_run is True
    )

    return ok, "adapter preserves execution block"


def _check_forbidden_execution_surface() -> tuple[bool, str]:
    adapter_path = (
        ROOT
        / "guardian_hunter"
        / "authorization"
        / "decision_response_adapter.py"
    )

    source = adapter_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden = {
        "exec",
        "eval",
        "system",
        "popen",
        "Popen",
        "call",
        "check_call",
        "check_output",
    }

    found = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            else:
                name = None

            if name in forbidden:
                found.append(name)

    return (
        len(found) == 0,
        "adapter execution surface contains no forbidden calls",
    )


def _check_audit_chain() -> tuple[bool, str]:
    engine = AuthorizationEngine()

    audit = engine.audit

    initial_length = len(audit.events)

    identity = Identity(
        actor_id="chain-auditor",
        role=Role.OBSERVER,
        active=True,
    )

    now = time.time()

    request = AuthorizationRequest(
        request_id="chain-request",
        authorization_id="chain-auth",
        actor_id="chain-auditor",
        action=Permission.VIEW,
        nonce="chain-nonce",
        issued_at=now,
        expires_at=now + 300,
    )

    decision = engine.authorize(identity, request)

    final_length = len(audit.events)

    chain_ok = audit.verify()

    ok = (
        decision.execution_allowed is False
        and final_length > initial_length
        and chain_ok is True
    )

    return ok, "authorization audit chain records decisions"


def _check_safety_constants() -> tuple[bool, str]:
    contract_path = (
        ROOT
        / "guardian_hunter"
        / "authorization"
        / "contract.py"
    )

    source = contract_path.read_text(encoding="utf-8")

    missing = [
        name
        for name, expected in SAFETY.items()
        if f"{name} = {expected}" not in source
    ]

    return (
        len(missing) == 0,
        "all five safety invariants remain defined as True",
    )


def run_audit() -> int:
    print("GUARDIAN HUNTER — AUTHORIZATION TRACEABILITY AUDIT v1")
    print("=" * 64)

    checks = [
        ("FAIL-CLOSED", _check_fail_closed),
        ("ACTOR BINDING", _check_actor_binding),
        ("ANTI-REPLAY", _check_replay),
        ("EXPIRATION", _check_expiration),
        ("PERMISSION BOUNDARY", _check_permission_boundary),
        ("HUMAN REVIEW", _check_human_review),
        ("ADAPTER PATH", _check_adapter_path),
        ("EXECUTION SURFACE", _check_forbidden_execution_surface),
        ("AUDIT CHAIN", _check_audit_chain),
        ("SAFETY INVARIANTS", _check_safety_constants),
    ]

    failures = []

    for name, function in checks:
        try:
            passed, detail = function()
        except Exception as exc:
            passed = False
            detail = f"exception: {exc}"

        status = "OK" if passed else "FAILED"

        print(f"{name}: {status}")
        print(f"  {detail}")

        if not passed:
            failures.append(name)

    print()
    print("READ_ONLY: True")
    print("DRY_RUN: True")
    print("REAL_EXECUTION_BLOCKED: True")
    print("HUMAN_REVIEW_REQUIRED: True")
    print("RESPONSE_LOCKED: True")
    print("REAL EXECUTION: BLOCKED")

    print()

    if failures:
        print("AUDIT STATE: TRACEABILITY_REVIEW_REQUIRED")
        print("FAILED CHECKS:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("=" * 64)
    print("AUDIT STATE: AUTHORIZATION_TRACEABILITY_OK")
    print("=" * 64)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_audit())
