"""Guardian Hunter — Controlled Security State Machine.

State flow:

    OBSERVE -> ANALYZE -> CANDIDATE
                           |       |
                        reject   authorize()
                           |       |
                           v       v
                       REJECTED AUTHORIZED
                                    |
                                    v
                                COMPLETED

AUTHORIZED cannot be reached through the generic transition()
function. It requires authorize_candidate() with verified evidence,
established trust and explicit human provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import FrozenSet

from guardian_hunter.evidence.persistence import EvidenceStore
from guardian_hunter.security.trust_root import TrustResult


class Mode(str, Enum):
    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    CANDIDATE = "CANDIDATE"
    AUTHORIZED = "AUTHORIZED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Capability(str, Enum):
    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    WRITE_FAILURE_EVIDENCE = "WRITE_FAILURE_EVIDENCE"
    CREATE_CANDIDATE = "CREATE_CANDIDATE"
    APPROVED_RESPONSE = "APPROVED_RESPONSE"


class TransitionError(RuntimeError):
    pass


class AuthorizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    evidence_id: str
    created_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AuthorizationProvenance:
    candidate_id: str
    evidence_id: str
    approver: str
    reason: str
    authorized_at: datetime


def capabilities_for(
    *,
    trust: TrustResult,
    mode: Mode,
) -> FrozenSet[Capability]:

    # UNTRUSTED has deliberately tiny capabilities.
    if not trust.trusted:
        return frozenset({
            Capability.OBSERVE,
            Capability.WRITE_FAILURE_EVIDENCE,
        })

    table = {
        Mode.OBSERVE: frozenset({
            Capability.OBSERVE,
        }),

        Mode.ANALYZE: frozenset({
            Capability.OBSERVE,
            Capability.ANALYZE,
        }),

        Mode.CANDIDATE: frozenset({
            Capability.OBSERVE,
            Capability.ANALYZE,
            Capability.CREATE_CANDIDATE,
        }),

        Mode.AUTHORIZED: frozenset({
            Capability.APPROVED_RESPONSE,
        }),

        Mode.COMPLETED: frozenset(),
        Mode.REJECTED: frozenset(),
    }

    return table[mode]


_TRANSITIONS = {
    Mode.OBSERVE: {Mode.ANALYZE},
    Mode.ANALYZE: {Mode.CANDIDATE},
    Mode.CANDIDATE: {Mode.REJECTED},

    # AUTHORIZED is reached ONLY through authorize_candidate().
    Mode.AUTHORIZED: {Mode.COMPLETED},

    Mode.COMPLETED: set(),
    Mode.REJECTED: set(),
}


def transition(
    current: Mode,
    target: Mode,
) -> Mode:

    if target not in _TRANSITIONS[current]:
        raise TransitionError(
            f"illegal transition: {current.value} -> {target.value}"
        )

    return target


def authorize_candidate(
    *,
    current: Mode,
    candidate: Candidate,
    trust: TrustResult,
    evidence_store: EvidenceStore,
    approver: str,
    reason: str,
    now: datetime | None = None,
) -> tuple[Mode, AuthorizationProvenance]:

    if current is not Mode.CANDIDATE:
        raise AuthorizationError(
            "authorization requires CANDIDATE state"
        )

    if not trust.trusted:
        raise AuthorizationError(
            "authorization forbidden while UNTRUSTED"
        )

    if not candidate.candidate_id.strip():
        raise AuthorizationError(
            "candidate_id is required"
        )

    if not candidate.evidence_id.strip():
        raise AuthorizationError(
            "evidence_id is required"
        )

    if not approver.strip():
        raise AuthorizationError(
            "approver is required"
        )

    if not reason.strip():
        raise AuthorizationError(
            "authorization reason is required"
        )

    current_time = now or datetime.now(timezone.utc)

    if current_time.tzinfo is None:
        raise AuthorizationError(
            "authorization timestamp must be timezone-aware"
        )

    if candidate.created_at.tzinfo is None:
        raise AuthorizationError(
            "candidate creation time must be timezone-aware"
        )

    if candidate.expires_at.tzinfo is None:
        raise AuthorizationError(
            "candidate expiry must be timezone-aware"
        )

    if candidate.expires_at <= candidate.created_at:
        raise AuthorizationError(
            "invalid candidate lifetime"
        )

    if current_time < candidate.created_at:
        raise AuthorizationError(
            "candidate is not yet valid"
        )

    if current_time >= candidate.expires_at:
        raise AuthorizationError(
            "candidate has expired"
        )

    # Do not trust a caller-supplied boolean.
    # Ask the persistent evidence store itself.
    if not evidence_store.contains_verified(
        candidate.evidence_id
    ):
        raise AuthorizationError(
            "verified evidence does not exist"
        )

    provenance = AuthorizationProvenance(
        candidate_id=candidate.candidate_id,
        evidence_id=candidate.evidence_id,
        approver=approver,
        reason=reason,
        authorized_at=current_time,
    )

    return Mode.AUTHORIZED, provenance
