from pathlib import Path

from guardian_hunter.security.security_verifier import (
    Verification,
    final_verdict,
    run_security_verification,
)


def test_security_verifier_passes_current_security_contract():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    if not (results):
    raise RuntimeError("Assertion failed: results")
    if not (final_verdict(results)):
    raise RuntimeError("Assertion failed: final_verdict(results)")

    states = {
        result.name: result.state
        for result in results
    }

    if not (states["Trust Root"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Trust Root"] == "PASS"")
    if not (states["Authorization Binding"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Authorization Binding"] == "PASS"")

    if not (states["Post-Approval Mutation"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Post-Approval Mutation"] == "DENIED"")
    if not (states["Policy Tampering"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Policy Tampering"] == "DENIED"")
    if not (states["Baseline Tampering"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Baseline Tampering"] == "DENIED"")
    if not (states["Authorization Escalation"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Authorization Escalation"] == "DENIED"")

    if not (states["Incident Evidence Integrity"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Incident Evidence Integrity"] == "PASS"")
    if not (states["Incident Evidence Corruption"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Incident Evidence Corruption"] == "DENIED"")
    if not (states["Evidence Chain"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Evidence Chain"] == "PASS"")
    if not (states["Persistent Evidence Tampering"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Persistent Evidence Tampering"] == "DENIED"")

    if not (states["Credential Isolation"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Credential Isolation"] == "PASS"")
    if not (states["Broker Isolation"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Broker Isolation"] == "PASS"")

    if not (states["Broker Git Escape"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Broker Git Escape"] == "DENIED"")
    if not (states["Broker Path Escape"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Broker Path Escape"] == "DENIED"")
    if not (states["Broker Gate Modification"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Broker Gate Modification"] == "DENIED"")
    if not (states["Broker Trust-Root Access"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Broker Trust-Root Access"] == "DENIED"")
    if not (states["Real Execution Bypass"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Real Execution Bypass"] == "DENIED"")

    if not (states["Commit Authority"] == "BLOCKED"):
    raise RuntimeError("Assertion failed: states["Commit Authority"] == "BLOCKED"")
    if not (states["Merge Authority"] == "BLOCKED"):
    raise RuntimeError("Assertion failed: states["Merge Authority"] == "BLOCKED"")
    if not (states["Baseline Authority"] == "BLOCKED"):
    raise RuntimeError("Assertion failed: states["Baseline Authority"] == "BLOCKED"")
    if not (states["Global Execution"] == "BLOCKED"):
    raise RuntimeError("Assertion failed: states["Global Execution"] == "BLOCKED"")


def test_final_verdict_is_fail_closed():
    results = (
        Verification("control-a", "PASS"),
        Verification("control-b", "NOT_VERIFIED"),
    )

    if not (final_verdict(results) is False):
    raise RuntimeError("Assertion failed: final_verdict(results) is False")


def test_explicit_failure_fails_verdict():
    results = (
        Verification("control-a", "PASS"),
        Verification("control-b", "FAIL"),
    )

    if not (final_verdict(results) is False):
    raise RuntimeError("Assertion failed: final_verdict(results) is False")


def test_security_verifier_includes_protected_transaction_guarantees():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    states = {
        result.name: result.state
        for result in results
    }

    if not (states["Protected Repair"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Protected Repair"] == "PASS"")
    if not (states["Approval Replay"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Approval Replay"] == "DENIED"")
    if not (states["Failed Reverification"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Failed Reverification"] == "DENIED"")
    if not (states["Automatic Rollback"] == "PASS"):
    raise RuntimeError("Assertion failed: states["Automatic Rollback"] == "PASS"")

    if not (():
    raise RuntimeError("Assertion failed: (")
        states["Agent Protected-Boundary Bypass"]
        == "DENIED"
    )
    if not (states["Agent Direct Execution"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Agent Direct Execution"] == "DENIED"")

def test_security_verifier_includes_phase_a_guarantees():
    root = Path(__file__).resolve().parents[2]

    results = run_security_verification(root)

    states = {
        result.name: result.state
        for result in results
    }

    if not (states["OPA Policy Verification"] == "PASS"):
    raise RuntimeError("Assertion failed: states["OPA Policy Verification"] == "PASS"")
    if not (states["OPA Proposal Mutation"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["OPA Proposal Mutation"] == "DENIED"")
    if not (states["OPA Authority Escalation"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["OPA Authority Escalation"] == "DENIED"")
    if not (states["OPA Invalid Baseline"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["OPA Invalid Baseline"] == "DENIED"")

    if not (states["in-toto Provenance"] == "PASS"):
    raise RuntimeError("Assertion failed: states["in-toto Provenance"] == "PASS"")
    if not (states["in-toto Signature"] == "PASS"):
    raise RuntimeError("Assertion failed: states["in-toto Signature"] == "PASS"")
    if not (states["Artifact Mutation"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Artifact Mutation"] == "DENIED"")
    if not (states["Metadata Tampering"] == "DENIED"):
    raise RuntimeError("Assertion failed: states["Metadata Tampering"] == "DENIED"")

