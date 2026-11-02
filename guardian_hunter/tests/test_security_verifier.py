from pathlib import Path

from guardian_hunter.security.security_verifier import (
    Verification,
    final_verdict,
    run_security_verification,
)


def test_security_verifier_passes_current_security_contract():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    assert results
    assert final_verdict(results)

    states = {
        result.name: result.state
        for result in results
    }

    assert states["Trust Root"] == "PASS"
    assert states["Authorization Binding"] == "PASS"

    assert states["Post-Approval Mutation"] == "DENIED"
    assert states["Policy Tampering"] == "DENIED"
    assert states["Baseline Tampering"] == "DENIED"
    assert states["Authorization Escalation"] == "DENIED"

    assert states["Incident Evidence Integrity"] == "PASS"
    assert states["Incident Evidence Corruption"] == "DENIED"
    assert states["Evidence Chain"] == "PASS"
    assert states["Persistent Evidence Tampering"] == "DENIED"

    assert states["Credential Isolation"] == "PASS"
    assert states["Broker Isolation"] == "PASS"

    assert states["Broker Git Escape"] == "DENIED"
    assert states["Broker Path Escape"] == "DENIED"
    assert states["Broker Gate Modification"] == "DENIED"
    assert states["Broker Trust-Root Access"] == "DENIED"
    assert states["Real Execution Bypass"] == "DENIED"

    assert states["Commit Authority"] == "BLOCKED"
    assert states["Merge Authority"] == "BLOCKED"
    assert states["Baseline Authority"] == "BLOCKED"
    assert states["Global Execution"] == "BLOCKED"


def test_final_verdict_is_fail_closed():
    results = (
        Verification("control-a", "PASS"),
        Verification("control-b", "NOT_VERIFIED"),
    )

    assert final_verdict(results) is False


def test_explicit_failure_fails_verdict():
    results = (
        Verification("control-a", "PASS"),
        Verification("control-b", "FAIL"),
    )

    assert final_verdict(results) is False


def test_security_verifier_includes_protected_transaction_guarantees():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    states = {
        result.name: result.state
        for result in results
    }

    assert states["Protected Repair"] == "PASS"
    assert states["Approval Replay"] == "DENIED"
    assert states["Failed Reverification"] == "DENIED"
    assert states["Automatic Rollback"] == "PASS"

    assert (
        states["Agent Protected-Boundary Bypass"]
        == "DENIED"
    )
    assert states["Agent Direct Execution"] == "DENIED"

def test_security_verifier_includes_phase_a_guarantees():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    states = {
        result.name: result.state
        for result in results
    }

    assert states["OPA Policy Verification"] == "PASS"
    assert states["OPA Proposal Mutation"] == "DENIED"
    assert states["OPA Authority Escalation"] == "DENIED"
    assert states["OPA Invalid Baseline"] == "DENIED"

    assert states["in-toto Provenance"] == "PASS"
    assert states["in-toto Signature"] == "PASS"
    assert states["Artifact Mutation"] == "DENIED"
    assert states["Metadata Tampering"] == "DENIED"

