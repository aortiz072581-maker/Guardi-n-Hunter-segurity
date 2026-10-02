"""Guardian Hunter — Authorization Contract v1.

This module defines authorization semantics only.

IMPORTANT SAFETY INVARIANTS:
    READ_ONLY = True
    DRY_RUN = True
    REAL_EXECUTION_BLOCKED = True
    HUMAN_REVIEW_REQUIRED = True
    RESPONSE_LOCKED = True

Authorization approval NEVER enables real execution.
All unknown, invalid, expired, replayed, or unsafe requests fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from time import time
from typing import FrozenSet

from guardian_hunter.security.trust_root import TrustResult


# ==============================================================
# NON-NEGOTIABLE SAFETY INVARIANTS
# ==============================================================

READ_ONLY = True
DRY_RUN = True
REAL_EXECUTION_BLOCKED = True
HUMAN_REVIEW_REQUIRED = True
RESPONSE_LOCKED = True


class Role(str, Enum):
    OBSERVER = "OBSERVER"
    ANALYST = "ANALYST"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"


class Permission(str, Enum):
    VIEW = "VIEW"
    ANALYZE = "ANALYZE"
    REQUEST_RESPONSE = "REQUEST_RESPONSE"
    APPROVE_RESPONSE = "APPROVE_RESPONSE"
    VIEW_AUDIT = "VIEW_AUDIT"


class AuthorizationState(str, Enum):
    DENIED = "DENIED"
    APPROVED = "APPROVED"
    EXPIRED = "EXPIRED"
    REPLAYED = "REPLAYED"
    INVALID = "INVALID"


# No permission in this contract can enable real execution.
ROLE_PERMISSIONS: dict[Role, FrozenSet[Permission]] = {
    Role.OBSERVER: frozenset({
        Permission.VIEW,
    }),
    Role.ANALYST: frozenset({
        Permission.VIEW,
        Permission.ANALYZE,
        Permission.VIEW_AUDIT,
    }),
    Role.OPERATOR: frozenset({
        Permission.VIEW,
        Permission.ANALYZE,
        Permission.REQUEST_RESPONSE,
        Permission.VIEW_AUDIT,
    }),
    Role.ADMIN: frozenset({
        Permission.VIEW,
        Permission.ANALYZE,
        Permission.REQUEST_RESPONSE,
        Permission.APPROVE_RESPONSE,
        Permission.VIEW_AUDIT,
    }),
}


@dataclass(frozen=True)
class Identity:
    """Authenticated actor identity."""

    actor_id: str
    role: Role
    active: bool = True


@dataclass(frozen=True)
class AuthorizationRequest:
    """A single authorization request."""

    request_id: str
    authorization_id: str
    actor_id: str
    action: Permission
    nonce: str
    issued_at: float
    expires_at: float
    requires_human_review: bool = True


@dataclass(frozen=True)
class AuthorizationDecision:
    """Fail-closed authorization result."""

    state: AuthorizationState
    authorized: bool
    request_id: str
    authorization_id: str
    actor_id: str
    action: Permission | None
    reason: str

    # These fields intentionally remain hard-blocked.
    execution_allowed: bool = False
    real_execution_blocked: bool = True
    read_only: bool = True
    dry_run: bool = True
    human_review_required: bool = True
    response_locked: bool = True


@dataclass(frozen=True)
class AuditEvent:
    """Tamper-evident audit event."""

    sequence: int
    timestamp: float
    event_type: str
    request_id: str
    actor_id: str
    state: str
    previous_hash: str
    event_hash: str


@dataclass
class AuthorizationAudit:
    """In-memory append-only audit chain for the contract layer."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(
        self,
        *,
        event_type: str,
        request_id: str,
        actor_id: str,
        state: AuthorizationState,
        timestamp: float | None = None,
    ) -> AuditEvent:
        ts = time() if timestamp is None else timestamp

        previous_hash = (
            self.events[-1].event_hash
            if self.events
            else "GENESIS"
        )

        sequence = len(self.events) + 1

        payload = "|".join([
            str(sequence),
            f"{ts:.6f}",
            event_type,
            request_id,
            actor_id,
            state.value,
            previous_hash,
        ])

        event_hash = sha256(
            payload.encode("utf-8")
        ).hexdigest()

        event = AuditEvent(
            sequence=sequence,
            timestamp=ts,
            event_type=event_type,
            request_id=request_id,
            actor_id=actor_id,
            state=state.value,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        self.events.append(event)
        return event

    def verify(self) -> bool:
        """Verify the complete audit chain."""

        previous = "GENESIS"

        for expected_sequence, event in enumerate(
            self.events,
            start=1,
        ):
            if event.sequence != expected_sequence:
                return False

            if event.previous_hash != previous:
                return False

            payload = "|".join([
                str(event.sequence),
                f"{event.timestamp:.6f}",
                event.event_type,
                event.request_id,
                event.actor_id,
                event.state,
                event.previous_hash,
            ])

            expected_hash = sha256(
                payload.encode("utf-8")
            ).hexdigest()

            if event.event_hash != expected_hash:
                return False

            previous = event.event_hash

        return True


class AuthorizationEngine:
    """Fail-closed authorization engine.

    This engine evaluates authorization only.
    It does not execute actions.
    """

    def __init__(
        self,
        *,
        trust_result: TrustResult | None = None,
    ) -> None:
        self._used_nonces: set[str] = set()
        self.audit = AuthorizationAudit()
        self._trust_result = trust_result

    def authorize(
        self,
        identity: Identity | None,
        request: AuthorizationRequest | None,
        *,
        now: float | None = None,
    ) -> AuthorizationDecision:
        current = time() if now is None else now

        # ------------------------------------------------------
        # FAIL-CLOSED: malformed identity
        # ------------------------------------------------------
        if identity is None:
            return self._deny(
                request,
                AuthorizationState.INVALID,
                "identity missing",
            )

        if not identity.active:
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "identity inactive",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # FAIL-CLOSED: malformed request
        # ------------------------------------------------------
        if request is None:
            return self._deny(
                None,
                AuthorizationState.INVALID,
                "authorization request missing",
                identity.actor_id,
            )

        if not request.request_id:
            return self._deny(
                request,
                AuthorizationState.INVALID,
                "request_id missing",
                identity.actor_id,
            )

        if not request.authorization_id:
            return self._deny(
                request,
                AuthorizationState.INVALID,
                "authorization_id missing",
                identity.actor_id,
            )

        if not request.nonce:
            return self._deny(
                request,
                AuthorizationState.INVALID,
                "nonce missing",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Identity binding
        # ------------------------------------------------------
        if request.actor_id != identity.actor_id:
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "request actor does not match identity",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Time validation
        # ------------------------------------------------------
        if request.expires_at <= request.issued_at:
            return self._deny(
                request,
                AuthorizationState.INVALID,
                "invalid authorization lifetime",
                identity.actor_id,
            )

        if current < request.issued_at:
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "authorization is not yet valid",
                identity.actor_id,
            )

        if current >= request.expires_at:
            return self._deny(
                request,
                AuthorizationState.EXPIRED,
                "authorization expired",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Anti-replay
        # ------------------------------------------------------
        if request.nonce in self._used_nonces:
            return self._deny(
                request,
                AuthorizationState.REPLAYED,
                "nonce already used",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Permission validation
        # ------------------------------------------------------
        allowed_permissions = ROLE_PERMISSIONS.get(
            identity.role,
            frozenset(),
        )

        if request.action not in allowed_permissions:
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "role lacks requested permission",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Human review remains mandatory.
        # Authorization approval does NOT bypass review.
        # ------------------------------------------------------
        if not request.requires_human_review:
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "human review requirement missing",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Non-negotiable safety gate.
        # ------------------------------------------------------
        if not self._safety_invariants_hold():
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "safety invariants failed",
                identity.actor_id,
            )

        # ------------------------------------------------------
        # RESPONSE TRUST GATE
        # ------------------------------------------------------
        # Structural validation, expiration, replay, permissions,
        # human review and safety invariants have already passed.
        #
        # Response authorization requires an explicit verified
        # Trust Root. Observation/analysis remain compatible with
        # the migration path.
        response_permissions = {
            Permission.REQUEST_RESPONSE,
            Permission.APPROVE_RESPONSE,
        }

        if request.action in response_permissions:
            if self._trust_result is None:
                return self._deny(
                    request,
                    AuthorizationState.DENIED,
                    "trust root required for response authorization",
                    identity.actor_id,
                )

            if not self._trust_result.trusted:
                return self._deny(
                    request,
                    AuthorizationState.DENIED,
                    "trust root verification failed: "
                    + self._trust_result.reason,
                    identity.actor_id,
                )

        # If a Trust Root was explicitly supplied for any other
        # authorization operation, a failed verification remains
        # fail-closed.
        if (
            self._trust_result is not None
            and not self._trust_result.trusted
        ):
            return self._deny(
                request,
                AuthorizationState.DENIED,
                "trust root verification failed: "
                + self._trust_result.reason,
                identity.actor_id,
            )

        # ------------------------------------------------------
        # Commit anti-replay nonce
        # ------------------------------------------------------
        # A nonce becomes consumed only after all authorization
        # gates, including Trust Root, have succeeded.
        self._used_nonces.add(request.nonce)

        decision = AuthorizationDecision(
            state=AuthorizationState.APPROVED,
            authorized=True,
            request_id=request.request_id,
            authorization_id=request.authorization_id,
            actor_id=identity.actor_id,
            action=request.action,
            reason="authorization policy satisfied",
            execution_allowed=False,
            real_execution_blocked=True,
            read_only=True,
            dry_run=True,
            human_review_required=True,
            response_locked=True,
        )

        self.audit.append(
            event_type="AUTHORIZATION_APPROVED",
            request_id=request.request_id,
            actor_id=identity.actor_id,
            state=AuthorizationState.APPROVED,
            timestamp=current,
        )

        return decision

    def _deny(
        self,
        request: AuthorizationRequest | None,
        state: AuthorizationState,
        reason: str,
        actor_id: str = "",
    ) -> AuthorizationDecision:

        request_id = (
            request.request_id
            if request is not None
            else ""
        )

        authorization_id = (
            request.authorization_id
            if request is not None
            else ""
        )

        action = (
            request.action
            if request is not None
            else None
        )

        self.audit.append(
            event_type="AUTHORIZATION_DENIED",
            request_id=request_id,
            actor_id=actor_id,
            state=state,
        )

        return AuthorizationDecision(
            state=state,
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

    @staticmethod
    def _safety_invariants_hold() -> bool:
        return all([
            READ_ONLY is True,
            DRY_RUN is True,
            REAL_EXECUTION_BLOCKED is True,
            HUMAN_REVIEW_REQUIRED is True,
            RESPONSE_LOCKED is True,
        ])
