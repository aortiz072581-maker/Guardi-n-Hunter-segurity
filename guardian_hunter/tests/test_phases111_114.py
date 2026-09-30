"""Integration tests for Guardian Hunter phases 111 → 114."""

from guardian_hunter.governance.phase111_response_governance import (
    build_response_governance,
)
from guardian_hunter.verification.phase112_response_chain import (
    build_verification_chain,
)
from guardian_hunter.governance.phase113_response_audit import (
    build_response_audit,
)
from guardian_hunter.governance.phase114_response_gate import (
    build_release_gate,
)


def test_phase111_governance():
    governance = build_response_governance()

    assert governance.read_only is True
    assert governance.dry_run is True
    assert governance.execution_allowed is False
    assert governance.human_review_required is True
    assert governance.response_locked is True

    assert governance.state == "DEFENSIVE_RESPONSE_GOVERNANCE_HARDENED"
    assert governance.score == 100


def test_phase112_verification():
    verification = build_verification_chain(
        {
            "phase": "111-114",
            "read_only": True,
            "dry_run": True,
            "execution_allowed": False,
        }
    )

    assert verification.state == "DEFENSIVE_RESPONSE_VERIFICATION_CHAIN_VALID"
    assert verification.score == 100
    assert len(verification.digest) == 64


def test_phase113_audit():
    audit = build_response_audit()

    audit.record("PHASE_111_GOVERNANCE_OK")
    audit.record("PHASE_112_VERIFICATION_OK")

    assert audit.state == "DEFENSIVE_RESPONSE_AUDIT_CONTINUOUS"
    assert audit.score == 100
    assert audit.execution_allowed is False
    assert len(audit.events) == 2


def test_phase114_release_gate():
    governance = build_response_governance()

    verification = build_verification_chain(
        {
            "phase": "111-114",
            "governance": governance.state,
        }
    )

    audit = build_response_audit()
    audit.record("PHASE_111_OK")
    audit.record("PHASE_112_OK")
    audit.record("PHASE_113_OK")

    gate = build_release_gate(
        governance_state=governance.state,
        verification_state=verification.state,
        audit_state=audit.state,
    )

    assert gate.read_only is True
    assert gate.dry_run is True
    assert gate.execution_allowed is False
    assert gate.human_review_required is True
    assert gate.response_locked is True

    assert gate.state == "DEFENSIVE_RESPONSE_RELEASE_GATE_READY"
    assert gate.score == 100


def test_real_execution_remains_blocked():
    governance = build_response_governance()

    assert governance.execution_allowed is False
    assert governance.read_only is True
    assert governance.dry_run is True
