"""Cryptographic authorization binding for Guardian Hunter.

Binds one human authorization to the exact:
    proposal
    policy
    trusted baseline

This module grants no execution authority.
Any missing, malformed, or changed binding fails closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
import json
import re
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def _strict_json(value: Any, *, depth: int = 0) -> None:
    """Reject lossy JSON conversions and ambiguous inputs before hashing."""
    import math
    if depth > 64:
        raise ValueError("CANONICAL_DEPTH_EXCEEDED")
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("NONFINITE_NUMBER")
        return
    if type(value) is list:
        for item in value:
            _strict_json(item, depth=depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("CANONICAL_KEYS_MUST_BE_STRINGS")
            _strict_json(item, depth=depth + 1)
        return
    raise TypeError("UNSUPPORTED_CANONICAL_TYPE")


def canonical_hash(value: Any) -> str:
    """Return deterministic SHA-256 for a JSON-compatible value."""

    _strict_json(value)
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class AuthorizationBinding:
    """Exact security context approved by a human."""

    proposal_hash: str
    policy_hash: str
    baseline: str

    execution_allowed: bool = False
    human_review_required: bool = True

    def validate(self) -> None:
        if not SHA256_RE.fullmatch(self.proposal_hash):
            raise PermissionError("INVALID_PROPOSAL_HASH")

        if not SHA256_RE.fullmatch(self.policy_hash):
            raise PermissionError("INVALID_POLICY_HASH")

        if not GIT_SHA1_RE.fullmatch(self.baseline):
            raise PermissionError("INVALID_BASELINE")

        if self.execution_allowed:
            raise PermissionError("EXECUTION_AUTHORITY_FORBIDDEN")

        if not self.human_review_required:
            raise PermissionError("HUMAN_REVIEW_REQUIRED")


def create_binding(
    *,
    proposal_hash: str,
    policy: Any,
    baseline: str,
) -> AuthorizationBinding:
    """Create a binding without granting execution authority."""

    binding = AuthorizationBinding(
        proposal_hash=proposal_hash,
        policy_hash=canonical_hash(policy),
        baseline=baseline,
    )

    binding.validate()
    return binding


def verify_binding(
    binding: AuthorizationBinding,
    *,
    proposal_hash: str,
    policy: Any,
    baseline: str,
) -> bool:
    """Fail closed unless the complete approved context is unchanged."""

    binding.validate()

    if not SHA256_RE.fullmatch(proposal_hash):
        raise PermissionError("INVALID_CURRENT_PROPOSAL_HASH")

    if not GIT_SHA1_RE.fullmatch(baseline):
        raise PermissionError("INVALID_CURRENT_BASELINE")

    if not hmac.compare_digest(
        binding.proposal_hash,
        proposal_hash,
    ):
        raise PermissionError("PROPOSAL_HASH_MISMATCH")

    current_policy_hash = canonical_hash(policy)

    if not hmac.compare_digest(
        binding.policy_hash,
        current_policy_hash,
    ):
        raise PermissionError("POLICY_HASH_MISMATCH")

    if not hmac.compare_digest(
        binding.baseline,
        baseline,
    ):
        raise PermissionError("BASELINE_MISMATCH")

    return True
