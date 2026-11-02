"""Signed provenance verification for Guardian Hunter.

Security properties demonstrated here:

1. Provenance metadata is signed with an ephemeral Ed25519 key.
2. The corresponding public key verifies the in-toto metadata.
3. Product mutation after recording is detected by its recorded hash.
4. Signed metadata mutation invalidates its signature.

Private signing keys are never persisted by this module.
This module grants no execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
import hashlib

from in_toto.models.metadata import Metadata
from in_toto.runlib import in_toto_run
from securesystemslib.signer import CryptoSigner


@dataclass(frozen=True)
class ProvenanceResult:
    signed_provenance: bool
    signature_verified: bool
    artifact_mutation_denied: bool
    metadata_tampering_denied: bool


def in_toto_public_key(signer: CryptoSigner) -> dict[str, Any]:
    """Serialize an SSlib public key for in-toto verification.

    securesystemslib SSlibKey.to_dict() intentionally omits keyid,
    while in-toto Metadata.verify_signature() requires keyid in its
    public-key dictionary.
    """

    key = dict(signer.public_key.to_dict())
    key["keyid"] = signer.public_key.keyid

    required = {
        "keyid",
        "keytype",
        "scheme",
        "keyval",
    }

    if not required.issubset(key):
        raise PermissionError(
            "IN_TOTO_PUBLIC_KEY_INVALID"
        )

    return key


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def _extract_sha256(
    products: dict[str, Any],
    artifact_name: str,
) -> str:
    """Return the SHA-256 recorded by in-toto for one product."""

    candidates = (
        artifact_name,
        f"./{artifact_name}",
    )

    record = None

    for candidate in candidates:
        if candidate in products:
            record = products[candidate]
            break

    if record is None:
        matches = [
            value
            for key, value in products.items()
            if Path(key).name == artifact_name
        ]

        if len(matches) == 1:
            record = matches[0]

    if not isinstance(record, dict):
        raise PermissionError(
            "IN_TOTO_PRODUCT_NOT_RECORDED"
        )

    digest = record.get("sha256")

    if not isinstance(digest, str):
        raise PermissionError(
            "IN_TOTO_SHA256_MISSING"
        )

    if len(digest) != 64:
        raise PermissionError(
            "IN_TOTO_SHA256_INVALID"
        )

    return digest


def verify_product(
    metadata: Metadata,
    artifact: Path,
) -> bool:
    """Verify the current artifact against its signed product hash."""

    products = metadata.signed.products

    expected = _extract_sha256(
        products,
        artifact.name,
    )

    actual = sha256_file(artifact)

    if actual != expected:
        raise PermissionError(
            "IN_TOTO_PRODUCT_HASH_MISMATCH"
        )

    return True


def create_signed_provenance(
    workspace: Path,
) -> tuple[Metadata, CryptoSigner, Path]:
    """Create signed in-toto metadata using an ephemeral Ed25519 key."""

    workspace = Path(workspace).resolve()
    workspace.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact = workspace / "guardian-artifact.txt"
    artifact.write_bytes(
        b"guardian-hunter-phase-a\n"
    )

    signer = CryptoSigner.generate_ed25519()

    metadata = in_toto_run(
        name="guardian-phase-a",
        material_list=[],
        product_list=[artifact.name],
        link_cmd_args=[],
        base_path=str(workspace),
        metadata_directory=str(workspace),
        signer=signer,
    )

    if not isinstance(metadata, Metadata):
        raise PermissionError(
            "IN_TOTO_METADATA_NOT_RETURNED"
        )

    if not metadata.signatures:
        raise PermissionError(
            "IN_TOTO_UNSIGNED_METADATA"
        )

    metadata.verify_signature(
        in_toto_public_key(signer),
    )

    verify_product(
        metadata,
        artifact,
    )

    return metadata, signer, artifact


def run_provenance_verification() -> ProvenanceResult:
    """Execute deterministic provenance attacks in an isolated directory."""

    with TemporaryDirectory(
        prefix="guardian-in-toto-",
    ) as temporary:
        workspace = Path(temporary)

        metadata, signer, artifact = (
            create_signed_provenance(
                workspace,
            )
        )

        signature_verified = False

        metadata.verify_signature(
            in_toto_public_key(signer),
        )
        signature_verified = True

        artifact.write_bytes(
            b"guardian-hunter-phase-a-TAMPERED\n"
        )

        try:
            verify_product(
                metadata,
                artifact,
            )
        except PermissionError as exc:
            artifact_mutation_denied = (
                str(exc)
                == "IN_TOTO_PRODUCT_HASH_MISMATCH"
            )
        else:
            artifact_mutation_denied = False

        # Restore the legitimate artifact before attacking metadata.
        artifact.write_bytes(
            b"guardian-hunter-phase-a\n"
        )

        metadata_path = (
            workspace
            / "guardian-phase-a.link"
        )

        metadata.dump(
            str(metadata_path),
        )

        loaded = Metadata.load(
            str(metadata_path),
        )

        loaded.verify_signature(
            in_toto_public_key(signer),
        )

        products = loaded.signed.products

        if not products:
            raise PermissionError(
                "IN_TOTO_PRODUCTS_EMPTY"
            )

        product_name = next(iter(products))

        loaded.signed.products[
            product_name
        ]["sha256"] = "0" * 64

        try:
            loaded.verify_signature(
                in_toto_public_key(signer),
            )
        except Exception:
            metadata_tampering_denied = True
        else:
            metadata_tampering_denied = False

        return ProvenanceResult(
            signed_provenance=bool(
                metadata.signatures
            ),
            signature_verified=signature_verified,
            artifact_mutation_denied=(
                artifact_mutation_denied
            ),
            metadata_tampering_denied=(
                metadata_tampering_denied
            ),
        )
