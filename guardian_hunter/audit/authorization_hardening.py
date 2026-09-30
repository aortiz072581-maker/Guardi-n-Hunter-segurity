"""
Guardian Hunter — Authorization Hardening Audit

Purpose:
- Audit the authorization contract without modifying Phase 18.
- Verify fail-closed behavior.
- Verify unknown actions cannot be authorized.
- Verify permission boundaries.
- Verify replay protection.
- Verify expiration.
- Verify the five safety invariants.
- Confirm real execution remains blocked.

No execution engine.
No subprocess.
No shell commands.
No modification of Phase 18.
"""

from __future__ import annotations

import inspect
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from guardian_hunter.authorization.contract import (
    AuthorizationEngine,
    AuthorizationRequest,
    AuthorizationState,
    Identity,
    Permission,
    Role,
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    HUMAN_REVIEW_REQUIRED,
    RESPONSE_LOCKED,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _request(
    *,
    request_id: str = "req-hardening-001",
    authorization_id: str = "auth-hardening-001",
    actor_id: str = "operator-001",
    action: str = "REQUEST_RESPONSE",
    nonce: str = "nonce-hardening-001",
    issued_at: float | None = None,
    expires_at: float | None = None,
) -> AuthorizationRequest:
    now = time.time()

    if issued_at is None:
        issued_at = now - 1.0

    if expires_at is None:
        expires_at = now + 300.0

    return AuthorizationRequest(
        request_id=request_id,
        authorization_id=authorization_id,
        actor_id=actor_id,
        action=action,
        nonce=nonce,
        issued_at=issued_at,
        expires_at=expires_at,
        requires_human_review=True,
    )


def _identity(
    *,
    actor_id: str = "operator-001",
    role: Role = Role.OPERATOR,
    active: bool = True,
) -> Identity:
    return Identity(
        actor_id=actor_id,
        role=role,
        active=active,
    )


def _authorize(engine, identity, request):
    """
    Compatibility wrapper around the current engine API.

    The audit discovers the public authorization method instead
    of modifying the contract implementation.
    """
    method = getattr(engine, "authorize", None)

    if method is None:
        raise AssertionError("AuthorizationEngine.authorize() is missing")

    return method(identity, request)


def audit_safety_invariants() -> None:
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def audit_unknown_action_fails_closed() -> None:
    """
    Unknown actions must not silently acquire a valid permission.
    """

    engine = AuthorizationEngine()

    identity = _identity(role=Role.ADMIN)

    request = _request(
        request_id="req-unknown-001",
        authorization_id="auth-unknown-001",
        action="UNKNOWN_ACTION_NOT_DEFINED",
        nonce="nonce-unknown-001",
    )

    decision = _authorize(engine, identity, request)

    assert decision.authorized is False, (
        "Unknown action must fail closed"
    )

    assert decision.execution_allowed is False, (
        "Unknown action must never permit execution"
    )

    assert decision.state in {
        AuthorizationState.DENIED,
        AuthorizationState.INVALID,
    }, (
        f"Unexpected state for unknown action: {decision.state}"
    )


def audit_permission_boundaries() -> None:
    """
    Verify role boundaries.

    OBSERVER:
        VIEW only

    ANALYST:
        VIEW / ANALYZE / VIEW_AUDIT

    OPERATOR:
        VIEW / ANALYZE / REQUEST_RESPONSE / VIEW_AUDIT

    ADMIN:
        includes approval capability
    """

    cases = [
        (
            Role.OBSERVER,
            "REQUEST_RESPONSE",
            False,
        ),
        (
            Role.ANALYST,
            "REQUEST_RESPONSE",
            False,
        ),
        (
            Role.OPERATOR,
            "REQUEST_RESPONSE",
            True,
        ),
        (
            Role.OBSERVER,
            "ANALYZE",
            False,
        ),
        (
            Role.ANALYST,
            "ANALYZE",
            True,
        ),
        (
            Role.OPERATOR,
            "ANALYZE",
            True,
        ),
    ]

    for index, (role, action, expected) in enumerate(cases):
        engine = AuthorizationEngine()

        identity = _identity(
            actor_id=f"boundary-{index}",
            role=role,
        )

        request = _request(
            request_id=f"boundary-req-{index}",
            authorization_id=f"boundary-auth-{index}",
            actor_id=f"boundary-{index}",
            action=action,
            nonce=f"boundary-nonce-{index}",
        )

        decision = _authorize(engine, identity, request)

        assert decision.authorized is expected, (
            f"Permission boundary failure: "
            f"{role=} {action=} "
            f"expected={expected} "
            f"got={decision.authorized}"
        )

        # Hard execution block always applies.
        assert decision.execution_allowed is False


def audit_inactive_identity() -> None:
    engine = AuthorizationEngine()

    identity = _identity(
        actor_id="inactive-001",
        role=Role.ADMIN,
        active=False,
    )

    request = _request(
        request_id="inactive-req-001",
        authorization_id="inactive-auth-001",
        actor_id="inactive-001",
        action="REQUEST_RESPONSE",
        nonce="inactive-nonce-001",
    )

    decision = _authorize(engine, identity, request)

    assert decision.authorized is False
    assert decision.execution_allowed is False


def audit_actor_binding() -> None:
    engine = AuthorizationEngine()

    identity = _identity(
        actor_id="actor-A",
        role=Role.ADMIN,
    )

    request = _request(
        request_id="binding-req-001",
        authorization_id="binding-auth-001",
        actor_id="actor-B",
        action="REQUEST_RESPONSE",
        nonce="binding-nonce-001",
    )

    decision = _authorize(engine, identity, request)

    assert decision.authorized is False
    assert decision.execution_allowed is False


def audit_expiration() -> None:
    engine = AuthorizationEngine()

    now = time.time()

    identity = _identity(
        actor_id="expired-001",
        role=Role.ADMIN,
    )

    request = _request(
        request_id="expired-req-001",
        authorization_id="expired-auth-001",
        actor_id="expired-001",
        action="REQUEST_RESPONSE",
        nonce="expired-nonce-001",
        issued_at=now - 600.0,
        expires_at=now - 300.0,
    )

    decision = _authorize(engine, identity, request)

    assert decision.authorized is False
    assert decision.execution_allowed is False

    assert decision.state == AuthorizationState.EXPIRED


def audit_replay_protection() -> None:
    engine = AuthorizationEngine()

    identity = _identity(
        actor_id="replay-001",
        role=Role.ADMIN,
    )

    request = _request(
        request_id="replay-req-001",
        authorization_id="replay-auth-001",
        actor_id="replay-001",
        action="REQUEST_RESPONSE",
        nonce="replay-nonce-001",
    )

    first = _authorize(engine, identity, request)

    assert first.execution_allowed is False

    second = _authorize(engine, identity, request)

    assert second.authorized is False
    assert second.execution_allowed is False
    assert second.state == AuthorizationState.REPLAYED


def audit_human_review_required() -> None:
    engine = AuthorizationEngine()

    identity = _identity(
        actor_id="review-001",
        role=Role.ADMIN,
    )

    request = _request(
        request_id="review-req-001",
        authorization_id="review-auth-001",
        actor_id="review-001",
        action="REQUEST_RESPONSE",
        nonce="review-nonce-001",
    )

    # Build an explicitly invalid request instead of mutating it.
    # AuthorizationRequest is frozen/immutable by design.
    request = AuthorizationRequest(
        request_id="review-req-001-invalid",
        authorization_id="review-auth-001-invalid",
        actor_id="review-001",
        action="REQUEST_RESPONSE",
        nonce="review-nonce-001-invalid",
        issued_at=time.time() - 1.0,
        expires_at=time.time() + 300.0,
        requires_human_review=False,
    )

    decision = _authorize(engine, identity, request)

    assert decision.authorized is False
    assert decision.execution_allowed is False


def audit_execution_surface() -> None:
    """
    Authorization layer must not contain an execution surface.
    """

    contract = PROJECT_ROOT / "guardian_hunter" / "authorization" / "contract.py"

    text = contract.read_text(encoding="utf-8")

    forbidden = [
        "os.system(",
        "os.popen(",
        "subprocess.",
        "Popen(",
        "shell=True",
        "eval(",
        "exec(",
    ]

    hits = [item for item in forbidden if item in text]

    assert not hits, (
        f"Forbidden execution surface detected in authorization contract: {hits}"
    )


def audit_execution_gate() -> None:
    """
    Even a valid authorization decision must never authorize execution.
    """

    engine = AuthorizationEngine()

    identity = _identity(
        actor_id="gate-001",
        role=Role.ADMIN,
    )

    request = _request(
        request_id="gate-req-001",
        authorization_id="gate-auth-001",
        actor_id="gate-001",
        action="REQUEST_RESPONSE",
        nonce="gate-nonce-001",
    )

    decision = _authorize(engine, identity, request)

    assert decision.execution_allowed is False


def audit_engine_api() -> None:
    """
    Confirm the expected public authorization API exists.
    """

    engine = AuthorizationEngine()

    assert callable(getattr(engine, "authorize", None))

    signature = inspect.signature(engine.authorize)

    assert len(signature.parameters) >= 2


def run_audit() -> dict[str, str]:
    audit_safety_invariants()
    audit_engine_api()
    audit_unknown_action_fails_closed()
    audit_permission_boundaries()
    audit_inactive_identity()
    audit_actor_binding()
    audit_expiration()
    audit_replay_protection()
    audit_human_review_required()
    audit_execution_surface()
    audit_execution_gate()

    return {
        "state": "AUTHORIZATION_HARDENING_OK",
        "unknown_actions": "FAIL_CLOSED",
        "permission_boundaries": "OK",
        "inactive_identity": "DENIED",
        "actor_binding": "OK",
        "expiration": "OK",
        "replay_protection": "OK",
        "human_review": "REQUIRED",
        "execution_surface": "NONE",
        "execution_allowed": "FALSE",
        "real_execution": "BLOCKED",
    }


if __name__ == "__main__":
    result = run_audit()

    print("==============================================================")
    print("GUARDIAN HUNTER — AUTHORIZATION HARDENING AUDIT")
    print("==============================================================")

    for key, value in result.items():
        print(f"{key.upper()}: {value}")

    print("")
    print("READ_ONLY:", READ_ONLY)
    print("DRY_RUN:", DRY_RUN)
    print("REAL_EXECUTION_BLOCKED:", REAL_EXECUTION_BLOCKED)
    print("HUMAN_REVIEW_REQUIRED:", HUMAN_REVIEW_REQUIRED)
    print("RESPONSE_LOCKED:", RESPONSE_LOCKED)

    print("")
    print("AUTHORIZATION HARDENING: OK")
    print("REAL EXECUTION: BLOCKED")
    print("==============================================================")
