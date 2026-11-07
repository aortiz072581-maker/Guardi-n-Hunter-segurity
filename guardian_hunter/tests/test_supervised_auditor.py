from dataclasses import replace

import pytest

from guardian_hunter.auditor.findings import (
    Confidence,
    Finding,
    Severity,
    validate_findings,
)


def sample_finding() -> Finding:
    return Finding(
        finding_id="GH-001",
        severity=Severity.HIGH,
        confidence=Confidence.CONFIRMED,
        title="Example controlled finding",
        description="A security inconsistency was identified.",
        risk="The inconsistency could weaken a security invariant.",
        evidence=("evidence-1",),
        affected_files=("guardian_hunter/example.py",),
        proposed_fix="Prepare a human-reviewed correction.",
        required_tests=("test_security_invariant",),
    )


def test_finding_is_fail_closed():
    finding = sample_finding()

    finding.validate()

    assert finding.automatic_repair is False
    assert finding.automatic_approval is False
    assert finding.execution_allowed is False
    assert finding.merge_allowed is False
    assert finding.human_approval_required is True


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("automatic_repair", True, "AUTOMATIC_REPAIR_FORBIDDEN"),
        ("automatic_approval", True, "AUTOMATIC_APPROVAL_FORBIDDEN"),
        ("execution_allowed", True, "AUDITOR_EXECUTION_FORBIDDEN"),
        ("merge_allowed", True, "AUDITOR_MERGE_FORBIDDEN"),
        ("human_approval_required", False, "HUMAN_APPROVAL_REQUIRED"),
    ),
)
def test_finding_cannot_gain_authority(field, value, reason):
    finding = replace(sample_finding(), **{field: value})

    with pytest.raises(PermissionError, match=reason):
        finding.validate()


def test_duplicate_finding_ids_fail_closed():
    finding = sample_finding()

    with pytest.raises(ValueError, match="DUPLICATE_FINDING_ID"):
        validate_findings((finding, finding))


def test_valid_findings_are_accepted():
    assert validate_findings((sample_finding(),)) is True


def test_auditor_has_no_change_authority():
    from guardian_hunter.auditor import engine

    assert engine.AUDITOR_READ_ONLY is True
    assert engine.AUTOMATIC_REPAIR is False
    assert engine.AUTOMATIC_APPROVAL is False
    assert engine.EXECUTION_ALLOWED is False
    assert engine.MERGE_ALLOWED is False
    assert engine.HUMAN_APPROVAL_REQUIRED is True


def test_auditor_returns_valid_findings():
    from guardian_hunter.auditor.engine import audit

    findings = audit()

    assert isinstance(findings, tuple)
    assert validate_findings(findings) is True


def test_current_policy_has_no_false_positive():
    from guardian_hunter.auditor.engine import audit

    findings = audit()
    ids = {finding.finding_id for finding in findings}

    # The current containment and harness path policies agree.
    # The auditor must not manufacture GH-001.
    assert "GH-001" not in ids


def test_auditor_detects_injected_policy_divergence(monkeypatch):
    import guardian_hunter.auditor.engine as engine

    monkeypatch.setattr(
        engine,
        "HARNESS_PREFIXES",
        tuple(engine.HARNESS_PREFIXES)
        + ("guardian_hunter/injected_test_boundary/",),
    )

    findings = engine.audit()
    matches = [
        finding
        for finding in findings
        if finding.finding_id == "GH-001"
    ]

    assert len(matches) == 1

    finding = matches[0]

    assert finding.severity is Severity.HIGH
    assert finding.confidence is Confidence.CONFIRMED
    assert finding.automatic_repair is False
    assert finding.automatic_approval is False
    assert finding.execution_allowed is False
    assert finding.merge_allowed is False
    assert finding.human_approval_required is True

    assert any(
        "injected_test_boundary" in evidence
        for evidence in finding.evidence
    )


def test_extended_audit_confirms_auditor_boundary_is_protected():
    from guardian_hunter.auditor.engine import audit

    findings = audit()
    ids = {finding.finding_id for finding in findings}

    # GH-006 was human-approved and repaired.
    # It must not reappear while the Gate protects the auditor.
    assert "GH-006" not in ids


def test_gh006_reappears_if_auditor_protection_is_removed(monkeypatch):
    import guardian_hunter.auditor.engine as engine

    reduced_gate = tuple(
        prefix
        for prefix in engine.GATE_PREFIXES
        if str(prefix).replace("\\", "/").strip("/") + "/"
        != "guardian_hunter/auditor/"
    )

    monkeypatch.setattr(
        engine,
        "GATE_PREFIXES",
        reduced_gate,
    )

    findings = engine.audit()

    finding = next(
        item
        for item in findings
        if item.finding_id == "GH-006"
    )

    assert finding.severity is Severity.HIGH
    assert finding.confidence is Confidence.CONFIRMED
    assert finding.automatic_repair is False
    assert finding.automatic_approval is False
    assert finding.execution_allowed is False
    assert finding.merge_allowed is False
    assert finding.human_approval_required is True


def test_broker_environment_has_no_known_credentials():
    from guardian_hunter.harness.broker import (
        CREDENTIAL_NAMES,
        sanitized_environment,
    )

    env = sanitized_environment()

    assert not (set(env) & set(CREDENTIAL_NAMES))


def test_registered_providers_have_no_privileged_authority():
    from guardian_hunter.harness.providers import PROVIDERS

    for spec in PROVIDERS.values():
        assert spec.git_access is False
        assert spec.master_access is False
        assert spec.trust_root_access is False
        assert spec.credential_passthrough is False
        assert spec.autonomous_merge is False
        assert spec.gate_modification is False
        assert spec.human_review_required is True


def test_gate_protects_auditor_boundary():
    from guardian_hunter.gate.core import protected_change

    assert protected_change(
        "guardian_hunter/auditor/engine.py"
    ) is True

    assert protected_change(
        "guardian_hunter/auditor/findings.py"
    ) is True


def test_auditor_cannot_approve_own_changes():
    from guardian_hunter.gate.core import evaluate_candidate

    result = evaluate_candidate(
        ["guardian_hunter/auditor/engine.py"]
    )

    assert result.passed is False
    assert result.human_review_required is True
    assert result.agent_merge_allowed is False
    assert result.reason.startswith(
        "PROTECTED_BOUNDARY_CHANGED:"
    )
