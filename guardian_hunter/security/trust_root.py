"""Guardian Hunter — Trust Root.

Establishes whether policy + baseline may be trusted.

The runtime contains only the PUBLIC verification key.
The private signing key must remain outside the normal
Guardian Hunter runtime.

FAIL-CLOSED:
Any missing, malformed, modified, or unverifiable trust
material results in UNTRUSTED.
"""

from __future__ import annotations

import base64
import hashlib
import json

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PublicKey,
)


@dataclass(frozen=True)
class TrustResult:
    trusted: bool
    reason: str
    policy_id: str | None
    baseline_id: str | None
    verification_time: str


class TrustError(Exception):
    """Trust material could not be safely verified."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def load_public_key(path: Path) -> Ed25519PublicKey:
    data = path.read_bytes()

    try:
        key = serialization.load_pem_public_key(data)
    except (ValueError, TypeError) as exc:
        raise TrustError("invalid public verification key") from exc

    if not isinstance(key, Ed25519PublicKey):
        raise TrustError("verification key is not Ed25519")

    return key


def verify_signature(
    payload: bytes,
    signature_b64: str,
    public_key: Ed25519PublicKey,
) -> bool:
    try:
        signature = base64.b64decode(
            signature_b64,
            validate=True,
        )
        public_key.verify(signature, payload)
        return True

    except (InvalidSignature, ValueError):
        return False


def verify_manifest(
    *,
    manifest_path: Path,
    signature_path: Path,
    public_key_path: Path,
) -> dict[str, Any]:

    manifest_bytes = manifest_path.read_bytes()
    signature_text = signature_path.read_text(
        encoding="utf-8"
    ).strip()

    public_key = load_public_key(public_key_path)

    if not verify_signature(
        manifest_bytes,
        signature_text,
        public_key,
    ):
        raise TrustError(
            "manifest signature verification failed"
        )

    try:
        manifest = json.loads(
            manifest_bytes.decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TrustError("invalid signed manifest") from exc

    if not isinstance(manifest, dict):
        raise TrustError("manifest must be an object")

    required = {
        "policy_id",
        "baseline_id",
        "policy_sha256",
        "baseline_sha256",
    }

    missing = required.difference(manifest)

    if missing:
        raise TrustError(
            "manifest missing required fields: "
            + ", ".join(sorted(missing))
        )

    for field in required:
        if not isinstance(manifest[field], str):
            raise TrustError(
                f"manifest field {field!r} must be a string"
            )

    return manifest


def establish_trust(
    *,
    manifest_path: Path,
    signature_path: Path,
    public_key_path: Path,
    policy_path: Path,
    baseline_path: Path,
) -> TrustResult:
    """Verify signed trust metadata and referenced files.

    No exception from malformed trust material is allowed to
    accidentally establish trust.
    """

    policy_id = None
    baseline_id = None

    try:
        manifest = verify_manifest(
            manifest_path=Path(manifest_path),
            signature_path=Path(signature_path),
            public_key_path=Path(public_key_path),
        )

        policy_id = manifest["policy_id"]
        baseline_id = manifest["baseline_id"]

        actual_policy = sha256_file(
            Path(policy_path)
        )

        if actual_policy != manifest["policy_sha256"]:
            return TrustResult(
                trusted=False,
                reason="POLICY_VERIFICATION_FAILED",
                policy_id=policy_id,
                baseline_id=baseline_id,
                verification_time=_utc_now(),
            )

        actual_baseline = sha256_file(
            Path(baseline_path)
        )

        if actual_baseline != manifest["baseline_sha256"]:
            return TrustResult(
                trusted=False,
                reason="BASELINE_VERIFICATION_FAILED",
                policy_id=policy_id,
                baseline_id=baseline_id,
                verification_time=_utc_now(),
            )

        return TrustResult(
            trusted=True,
            reason="TRUST_ESTABLISHED",
            policy_id=policy_id,
            baseline_id=baseline_id,
            verification_time=_utc_now(),
        )

    except (
        OSError,
        TrustError,
        KeyError,
        TypeError,
    ) as exc:
        # Security boundary: fail closed.
        return TrustResult(
            trusted=False,
            reason=f"TRUST_ERROR:{type(exc).__name__}",
            policy_id=policy_id,
            baseline_id=baseline_id,
            verification_time=_utc_now(),
        )
