from pathlib import Path

import pytest

from guardian_hunter.provenance.in_toto_verifier import (
    in_toto_public_key,
    create_signed_provenance,
    run_provenance_verification,
    verify_product,
)


def test_signed_in_toto_provenance(tmp_path: Path):
    metadata, signer, artifact = (
        create_signed_provenance(
            tmp_path,
        )
    )

    assert metadata.signatures

    metadata.verify_signature(
        in_toto_public_key(signer),
    )

    assert verify_product(
        metadata,
        artifact,
    )


def test_artifact_mutation_is_denied(
    tmp_path: Path,
):
    metadata, _, artifact = (
        create_signed_provenance(
            tmp_path,
        )
    )

    artifact.write_bytes(
        b"ATTACKED\n"
    )

    with pytest.raises(
        PermissionError,
        match="IN_TOTO_PRODUCT_HASH_MISMATCH",
    ):
        verify_product(
            metadata,
            artifact,
        )


def test_metadata_tampering_breaks_signature(
    tmp_path: Path,
):
    metadata, signer, _ = (
        create_signed_provenance(
            tmp_path,
        )
    )

    product_name = next(
        iter(metadata.signed.products)
    )

    metadata.signed.products[
        product_name
    ]["sha256"] = "0" * 64

    with pytest.raises(Exception):
        metadata.verify_signature(
            in_toto_public_key(signer),
        )


def test_complete_provenance_attack_suite():
    result = run_provenance_verification()

    assert result.signed_provenance is True
    assert result.signature_verified is True

    assert (
        result.artifact_mutation_denied
        is True
    )

    assert (
        result.metadata_tampering_denied
        is True
    )
