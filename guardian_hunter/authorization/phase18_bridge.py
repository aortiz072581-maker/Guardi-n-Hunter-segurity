"""
Guardian Hunter
Phase 18 -> Authorization Contract DRY-RUN Bridge

IMPORTANT SAFETY PROPERTIES
---------------------------
This module does NOT execute responses.

It only translates a Phase 18 event into an authorization
request and evaluates that request through AuthorizationEngine.

Phase 18 files are NOT modified by this bridge.

Permanent invariants:
    READ_ONLY=True
    DRY_RUN=True
    REAL_EXECUTION_BLOCKED=True
    HUMAN_REVIEW_REQUIRED=True
    RESPONSE_LOCKED=True
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping

from guardian_hunter.authorization.contract import (
    AuthorizationDecision,
    AuthorizationEngine,
    AuthorizationRequest,
    Identity,
    Permission,
    Role,
    READ_ONLY,
    DRY_RUN,
    REAL_EXECUTION_BLOCKED,
    HUMAN_REVIEW_REQUIRED,
    RESPONSE_LOCKED,
)


@dataclass(frozen=True)
class Phase18AuthorizationResult:
    """
    Immutable result returned by the DRY-RUN bridge.

    The bridge can authorize a request for review, but it can
    never authorize real execution.
    """

    decision: AuthorizationDecision
    phase18_event_id: str
    bridge_mode: str = "DRY_RUN"

    @property
    def authorized(self) -> bool:
        return self.decision.authorized

    @property
    def execution_allowed(self) -> bool:
        # Hard safety override.
        return False


class Phase18AuthorizationBridge:
    """
    Isolated adapter between Phase 18 output and AuthorizationEngine.

    No Phase 18 implementation is imported for mutation.
    No response/action executor is called.
    """

    def __init__(self, engine: AuthorizationEngine | None = None):
        self.engine = engine or AuthorizationEngine()

    @staticmethod
    def _permission_from_action(action: str) -> Permission:
        """
        Convert a controlled Phase 18 action label into a permission.

        Unknown actions fail closed.
        """

        mapping = {
            "view": Permission.VIEW,
            "analyze": Permission.ANALYZE,
            "request_response": Permission.REQUEST_RESPONSE,
            "approve_response": Permission.APPROVE_RESPONSE,
            "view_audit": Permission.VIEW_AUDIT,
        }

        normalized = str(action).strip().lower()

        if normalized not in mapping:
            raise ValueError(
                f"unknown authorization action: {normalized!r}"
            )

        return mapping[normalized]

    @staticmethod
    def _validate_phase18_event(
        event: Mapping[str, Any],
    ) -> tuple[bool, str]:
        """
        Validate the minimum Phase 18 event contract.

        Missing/invalid fields fail closed.
        """

        if not isinstance(event, Mapping):
            return False, "invalid_phase18_event"

        event_id = event.get("event_id")
        actor_id = event.get("actor_id")
        role = event.get("role")
        action = event.get("action")

        if not event_id:
            return False, "missing_event_id"

        if not actor_id:
            return False, "missing_actor_id"

        if not role:
            return False, "missing_role"

        if not action:
            return False, "missing_action"

        try:
            Role(str(role).upper())
        except ValueError:
            return False, "invalid_role"

        return True, "valid"

    def authorize_phase18_event(
        self,
        event: Mapping[str, Any],
        *,
        now: float | None = None,
    ) -> Phase18AuthorizationResult:
        """
        Evaluate a Phase 18 event through Authorization Contract v1.

        This method performs authorization only.

        It NEVER executes a response.
        """

        valid, reason = self._validate_phase18_event(event)

        if not valid:
            decision = self._blocked_decision(
                reason=reason,
                request_id=str(event.get("request_id", "invalid")),
                authorization_id=str(
                    event.get("authorization_id", "invalid")
                ),
                actor_id=str(event.get("actor_id", "unknown")),
                action=str(event.get("action", "unknown")),
            )

            return Phase18AuthorizationResult(
                decision=decision,
                phase18_event_id=str(event.get("event_id", "invalid")),
            )

        actor_id = str(event["actor_id"])
        role = Role(str(event["role"]).upper())

        try:
            action = self._permission_from_action(
                str(event["action"])
            )
        except ValueError:
            decision = self._blocked_decision(
                reason="unknown_action",
                request_id=str(
                    event.get("request_id", "invalid")
                ),
                authorization_id=str(
                    event.get("authorization_id", "invalid")
                ),
                actor_id=actor_id,
                action=str(event["action"]),
            )

            return Phase18AuthorizationResult(
                decision=decision,
                phase18_event_id=str(event["event_id"]),
            )

        current = time.time() if now is None else float(now)

        issued_at = float(event.get("issued_at", current - 1.0))
        expires_at = float(event.get("expires_at", current + 60.0))

        request_id = str(
            event.get(
                "request_id",
                f"phase18-{event['event_id']}",
            )
        )

        authorization_id = str(
            event.get(
                "authorization_id",
                f"auth-{event['event_id']}",
            )
        )

        nonce = str(
            event.get(
                "nonce",
                f"nonce-{event['event_id']}",
            )
        )

        identity = Identity(
            actor_id=actor_id,
            role=role,
            active=bool(event.get("identity_active", True)),
        )

        request = AuthorizationRequest(
            request_id=request_id,
            authorization_id=authorization_id,
            actor_id=actor_id,
            action=action,
            nonce=nonce,
            issued_at=issued_at,
            expires_at=expires_at,
            requires_human_review=True,
        )

        decision = self.engine.authorize(
            identity,
            request,
            now=current,
        )

        return Phase18AuthorizationResult(
            decision=decision,
            phase18_event_id=str(event["event_id"]),
        )

    @staticmethod
    def _blocked_decision(
        *,
        reason: str,
        request_id: str,
        authorization_id: str,
        actor_id: str,
        action: str,
    ) -> AuthorizationDecision:
        """
        Construct a hard-blocked decision.

        Used when the Phase 18 event itself is invalid.
        """

        from guardian_hunter.authorization.contract import AuthorizationState

        return AuthorizationDecision(
            state=AuthorizationState.INVALID,
            authorized=False,
            request_id=request_id,
            authorization_id=authorization_id,
            actor_id=actor_id,
            action=action,
            reason=reason,
            execution_allowed=False,
            real_execution_blocked=True,
            read_only=True,
            dry_run=True,
            human_review_required=True,
            response_locked=True,
        )


def safety_invariants_hold() -> bool:
    """
    Independent bridge-level safety assertion.
    """

    return (
        READ_ONLY is True
        and DRY_RUN is True
        and REAL_EXECUTION_BLOCKED is True
        and HUMAN_REVIEW_REQUIRED is True
        and RESPONSE_LOCKED is True
    )
