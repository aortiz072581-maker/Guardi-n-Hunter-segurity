"""Integration tests for Guardian Hunter phases 127 → 130."""

from guardian_hunter.governance.phase127_attestation import build_attestation
from guardian_hunter.verification.phase128_attestation_integrity import (
    build_integrity,
)
from guardian_hunter.governance.phase129_consistency_lock import (
    build_consistency_lock,
)
from guardian_hunter.governance.phase130_master_gate import (
    build_master_gate,
)


def test_phase127_attestation():
    attestation = build_attestation()

    assert attestation.state == "DEFENSIVE_STATE_ATTESTATION_VALID"
    assert attestation.score == 100
    assert attestation.read_only is True
    assert attestation.dry_run is True
    assert attestation.human_review_required is True
    assert attestation.response_locked is True
    assert attestation.real_execution_blocked is True


def test_phase128_integrity():
    attestation = build_attestation()

    integrity = build_integrity(
        attestation_state=attestation.state,
        attestation_score=attestation.score,
    )

    assert integrity.state == "DEFENSIVE_ATTESTATION_INTEGRITY_VALID"
    assert integrity.score == 100
    assert len(integrity.digest) == 64


def test_phase129_consistency():
    attestation = build_attestation()

    integrity = build_integrity(
        attestation_state=attestation.state,
        attestation_score=attestation.score,
    )

    consistency = build_consistency_lock(
        attestation_state=attestation.state,
        integrity_state=integrity.state,
    )

    assert consistency.state == "DEFENSIVE_GOVERNANCE_CONSISTENCY_LOCKED"
    assert consistency.score == 100
    assert consistency.read_only is True
    assert consistency.dry_run is True
    assert consistency.human_review_required is True
    assert consistency.response_locked is True
    assert consistency.real_execution_blocked is True


def test_phase130_master():
    attestation = build_attestation()

    integrity = build_integrity(
        attestation_state=attestation.state,
        attestation_score=attestation.score,
    )

    consistency = build_consistency_lock(
        attestation_state=attestation.state,
        integrity_state=integrity.state,
    )

    gate = build_master_gate(
        attestation_state=attestation.state,
        integrity_state=integrity.state,
        consistency_state=consistency.state,
    )

    assert gate.state == "DEFENSIVE_ATTESTATION_MASTER_READY"
    assert gate.score == 100
    assert gate.response_score == 100
    assert gate.read_only is True
    assert gate.dry_run is True
    assert gate.human_review_required is True
    assert gate.response_locked is True
    assert gate.real_execution_blocked is True


def test_real_execution_remains_blocked():
    attestation = build_attestation()
    consistency = build_consistency_lock(
        attestation_state=attestation.state,
        integrity_state="DEFENSIVE_ATTESTATION_INTEGRITY_VALID",
    )

    assert attestation.real_execution_blocked is True
    assert consistency.real_execution_blocked is True
