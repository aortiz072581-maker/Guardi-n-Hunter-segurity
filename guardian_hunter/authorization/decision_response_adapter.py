"""
Guardian Hunter
Authorization → Decision/Response Controlled Adapter v1

Controlled integration layer:

    Identity
        ↓
    Authorization Contract
        ↓
    Authorization Decision
        ↓
    Decision / Response Planning
        ↓
    Human Review
        ↓
    REAL EXECUTION BLOCKED

This adapter NEVER executes an action.

Safety invariants:
    READ_ONLY=True
    DRY_RUN=True
    REAL_EXECUTION_BLOCKED=True
    HUMAN_REVIEW_REQUIRED=True
    RESPONSE_LOCKED=True
"""

from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any, Mapping

from guardian_hunter.authorization.contract import (
    AuthorizationEngine,
    AuthorizationRequest,
    AuthorizationState,
    Identity,
    Permission,
    Role,
)

from guardian_hunter.response.policy import (
    classify_response,
    build_policy_decision,
)

from guardian_hunter.response.orchestrator import (
    create_incident,
)


READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


@dataclass(frozen=True)
class ControlledIntegrationResult:
    """
    Immutable result of the controlled integration.

    No executable response is returned.
    """

    authorized: bool
    authorization_state: str
    authorization_id: str
    request_id: str
    actor_id: str
    action: str

    response_class: Any
    policy_decision: Any
    incident: Any

    execution_allowed: bool

    read_only: bool
    dry_run: bool
    real_execution_blocked: bool
    human_review_required: bool
    response_locked: bool

    reason: str


class AuthorizationDecisionResponseAdapter:
    """
    Controlled authorization → decision/response adapter.

    The adapter can prepare a response plan only after the
    authorization contract approves the requested operation.

    Even after approval:
        execution_allowed == False

    permanently for this adapter.
    """

    def __init__(
        self,
        authorization_engine: AuthorizationEngine | None = None,
    ) -> None:
        self._authorization_engine = (
            authorization_engine
            if authorization_engine is not None
            else AuthorizationEngine()
        )

    @staticmethod
    def _permission_from_action(action: str) -> Permission | None:
        """
        Explicit action mapping.

        Unknown actions fail closed.
        """

        mapping = {
            "view": Permission.VIEW,
            "analyze": Permission.ANALYZE,
            "request_response": Permission.REQUEST_RESPONSE,
            "approve_response": Permission.APPROVE_RESPONSE,
            "view_audit": Permission.VIEW_AUDIT,
        }

        return mapping.get(action)

    @staticmethod
    def _hard_block(
        *,
        authorization_state: AuthorizationState | str,
        authorization_id: str,
        request_id: str,
        actor_id: str,
        action: str,
        reason: str,
    ) -> ControlledIntegrationResult:
        """
        Universal fail-closed result.
        """

        return ControlledIntegrationResult(
            authorized=False,
            authorization_state=str(authorization_state),
            authorization_id=authorization_id,
            request_id=request_id,
            actor_id=actor_id,
            action=action,
            response_class=None,
            policy_decision=None,
            incident=None,
            execution_allowed=False,
            read_only=READ_ONLY,
            dry_run=DRY_RUN,
            real_execution_blocked=REAL_EXECUTION_BLOCKED,
            human_review_required=HUMAN_REVIEW_REQUIRED,
            response_locked=RESPONSE_LOCKED,
            reason=reason,
        )

    def authorize_and_prepare_response(
        self,
        *,
        actor_id: str,
        role: Role,
        action: str,
        request_id: str,
        authorization_id: str,
        nonce: str,
        risk_level: str,
        reason: str,
        target: str,
        risk_data: Mapping[str, Any] | None = None,
        issued_at: float | None = None,
        expires_at: float | None = None,
    ) -> ControlledIntegrationResult:
        """
        Authorize first, then prepare a response.

        No real execution is possible.

        Unknown action:
            DENIED

        Invalid identity:
            DENIED

        Expired request:
            DENIED

        Replay:
            DENIED

        Missing permission:
            DENIED

        Human review disabled:
            DENIED

        Safety invariant violation:
            DENIED
        """

        # --------------------------------------------------------------
        # GLOBAL SAFETY GATE
        # --------------------------------------------------------------

        if not READ_ONLY:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="READ_ONLY_INVARIANT_FAILED",
            )

        if not DRY_RUN:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="DRY_RUN_INVARIANT_FAILED",
            )

        if not REAL_EXECUTION_BLOCKED:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="REAL_EXECUTION_BLOCK_INVARIANT_FAILED",
            )

        if not HUMAN_REVIEW_REQUIRED:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="HUMAN_REVIEW_INVARIANT_FAILED",
            )

        if not RESPONSE_LOCKED:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="RESPONSE_LOCK_INVARIANT_FAILED",
            )

        # --------------------------------------------------------------
        # ACTION GATE
        # --------------------------------------------------------------

        permission = self._permission_from_action(action)

        if permission is None:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="UNKNOWN_ACTION_FAIL_CLOSED",
            )

        # --------------------------------------------------------------
        # IDENTITY
        # --------------------------------------------------------------

        try:
            identity = Identity(
                actor_id=actor_id,
                role=role,
                active=True,
            )
        except Exception as exc:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason=f"IDENTITY_INVALID:{type(exc).__name__}",
            )

        # --------------------------------------------------------------
        # AUTHORIZATION REQUEST
        # --------------------------------------------------------------

        now = time()

        if issued_at is None:
            issued_at = now

        if expires_at is None:
            expires_at = now + 300

        try:
            request = AuthorizationRequest(
                request_id=request_id,
                authorization_id=authorization_id,
                actor_id=actor_id,
                action=permission,
                nonce=nonce,
                issued_at=issued_at,
                expires_at=expires_at,
                requires_human_review=True,
            )
        except Exception as exc:
            return self._hard_block(
                authorization_state=AuthorizationState.INVALID,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason=f"AUTHORIZATION_REQUEST_INVALID:{type(exc).__name__}",
            )

        # --------------------------------------------------------------
        # AUTHORIZATION ENGINE
        # --------------------------------------------------------------

        try:
            authorization = self._authorization_engine.authorize(
                identity,
                request,
            )
        except Exception as exc:
            return self._hard_block(
                authorization_state=AuthorizationState.INVALID,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason=f"AUTHORIZATION_ENGINE_ERROR:{type(exc).__name__}",
            )

        authorization_state = getattr(
            authorization,
            "state",
            AuthorizationState.INVALID,
        )

        authorization_allowed = bool(
            getattr(
                authorization,
                "authorized",
                False,
            )
        )

        # --------------------------------------------------------------
        # AUTHORIZATION FAIL-CLOSED GATE
        # --------------------------------------------------------------

        if not authorization_allowed:
            return self._hard_block(
                authorization_state=authorization_state,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="AUTHORIZATION_DENIED",
            )

        # --------------------------------------------------------------
        # HARD SAFETY CHECK AFTER AUTHORIZATION
        # --------------------------------------------------------------

        if getattr(
            authorization,
            "execution_allowed",
            False,
        ) is not False:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="AUTHORIZATION_EXECUTION_GATE_VIOLATION",
            )

        # --------------------------------------------------------------
        # RESPONSE PLANNING
        #
        # This stage creates only a defensive plan.
        # It does NOT execute anything.
        # --------------------------------------------------------------

        try:
            response_class = classify_response(
                risk_level,
                authorized=True,
            )

            policy_decision = build_policy_decision(
                risk_level,
                reason,
                authorized=True,
            )

            incident = create_incident(
                risk_level,
                reason,
                target,
                authorized=True,
                risk_data=dict(risk_data or {}),
            )

        except Exception as exc:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason=f"RESPONSE_PLANNING_ERROR:{type(exc).__name__}",
            )

        # --------------------------------------------------------------
        # FINAL EXECUTION GATE
        #
        # This is deliberately hard-coded false.
        # Authorization can approve a response plan.
        # It can NEVER authorize actual execution here.
        # --------------------------------------------------------------

        execution_allowed = False

        if execution_allowed is not False:
            return self._hard_block(
                authorization_state=AuthorizationState.DENIED,
                authorization_id=authorization_id,
                request_id=request_id,
                actor_id=actor_id,
                action=action,
                reason="FINAL_EXECUTION_GATE_VIOLATION",
            )

        return ControlledIntegrationResult(
            authorized=True,
            authorization_state=str(authorization_state),
            authorization_id=authorization_id,
            request_id=request_id,
            actor_id=actor_id,
            action=action,
            response_class=response_class,
            policy_decision=policy_decision,
            incident=incident,
            execution_allowed=False,
            read_only=True,
            dry_run=True,
            real_execution_blocked=True,
            human_review_required=True,
            response_locked=True,
            reason="AUTHORIZED_RESPONSE_PLAN_READY_FOR_HUMAN_REVIEW",
        )

    def safety_invariants_hold(self) -> bool:
        return (
            READ_ONLY is True
            and DRY_RUN is True
            and REAL_EXECUTION_BLOCKED is True
            and HUMAN_REVIEW_REQUIRED is True
            and RESPONSE_LOCKED is True
        )


__all__ = [
    "READ_ONLY",
    "DRY_RUN",
    "REAL_EXECUTION_BLOCKED",
    "HUMAN_REVIEW_REQUIRED",
    "RESPONSE_LOCKED",
    "ControlledIntegrationResult",
    "AuthorizationDecisionResponseAdapter",
]
