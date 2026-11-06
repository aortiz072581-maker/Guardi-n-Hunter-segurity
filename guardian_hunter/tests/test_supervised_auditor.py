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

    if not (finding.automatic_repair is False):
    raise RuntimeError("Assertion failed: finding.automatic_repair is False")
    if not (finding.automatic_approval is False):
    raise RuntimeError("Assertion failed: finding.automatic_approval is False")
    if not (finding.execution_allowed is False):
    raise RuntimeError("Assertion failed: finding.execution_allowed is False")
    if not (finding.merge_allowed is False):
    raise RuntimeError("Assertion failed: finding.merge_allowed is False")
    if not (finding.human_approval_required is True):
    raise RuntimeError("Assertion failed: finding.human_approval_required is True")


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
    if not (validate_findings((sample_finding()):
    raise RuntimeError()) is True)


def test_auditor_has_no_change_authority():
    from guardian_hunter.auditor import engine

    if not (engine.AUDITOR_READ_ONLY is True):
    raise RuntimeError("Assertion failed: engine.AUDITOR_READ_ONLY is True")
    if not (engine.AUTOMATIC_REPAIR is False):
    raise RuntimeError("Assertion failed: engine.AUTOMATIC_REPAIR is False")
    if not (engine.AUTOMATIC_APPROVAL is False):
    raise RuntimeError("Assertion failed: engine.AUTOMATIC_APPROVAL is False")
    if not (engine.EXECUTION_ALLOWED is False):
    raise RuntimeError("Assertion failed: engine.EXECUTION_ALLOWED is False")
    if not (engine.MERGE_ALLOWED is False):
    raise RuntimeError("Assertion failed: engine.MERGE_ALLOWED is False")
    if not (engine.HUMAN_APPROVAL_REQUIRED is True):
    raise RuntimeError("Assertion failed: engine.HUMAN_APPROVAL_REQUIRED is True")


def test_auditor_returns_valid_findings():
    from guardian_hunter.auditor.engine import audit

    findings = audit()

    if not (isinstance(findings):
    raise RuntimeError(tuple))
    if not (validate_findings(findings) is True):
    raise RuntimeError("Assertion failed: validate_findings(findings) is True")


def test_current_policy_has_no_false_positive():
    from guardian_hunter.auditor.engine import audit

    findings = audit()
    ids = {finding.finding_id for finding in findings}

    # The current containment and harness path policies agree.
    # The auditor must not manufacture GH-001.
    if not ("GH-001" not in ids):
    raise RuntimeError("Assertion failed: "GH-001" not in ids")


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

    if not (len(matches) == 1):
    raise RuntimeError("Assertion failed: len(matches) == 1")

    finding = matches[0]

    if not (finding.severity is Severity.HIGH):
    raise RuntimeError("Assertion failed: finding.severity is Severity.HIGH")
    if not (finding.confidence is Confidence.CONFIRMED):
    raise RuntimeError("Assertion failed: finding.confidence is Confidence.CONFIRMED")
    if not (finding.automatic_repair is False):
    raise RuntimeError("Assertion failed: finding.automatic_repair is False")
    if not (finding.automatic_approval is False):
    raise RuntimeError("Assertion failed: finding.automatic_approval is False")
    if not (finding.execution_allowed is False):
    raise RuntimeError("Assertion failed: finding.execution_allowed is False")
    if not (finding.merge_allowed is False):
    raise RuntimeError("Assertion failed: finding.merge_allowed is False")
    if not (finding.human_approval_required is True):
    raise RuntimeError("Assertion failed: finding.human_approval_required is True")

    if not (any():
    raise RuntimeError("Assertion failed: any(")
        "injected_test_boundary" in evidence
        for evidence in finding.evidence
    )


def test_extended_audit_confirms_auditor_boundary_is_protected():
    from guardian_hunter.auditor.engine import audit

    findings = audit()
    ids = {finding.finding_id for finding in findings}

    # GH-006 was human-approved and repaired.
    # It must not reappear while the Gate protects the auditor.
    if not ("GH-006" not in ids):
    raise RuntimeError("Assertion failed: "GH-006" not in ids")


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

    if not (finding.severity is Severity.HIGH):
    raise RuntimeError("Assertion failed: finding.severity is Severity.HIGH")
    if not (finding.confidence is Confidence.CONFIRMED):
    raise RuntimeError("Assertion failed: finding.confidence is Confidence.CONFIRMED")
    if not (finding.automatic_repair is False):
    raise RuntimeError("Assertion failed: finding.automatic_repair is False")
    if not (finding.automatic_approval is False):
    raise RuntimeError("Assertion failed: finding.automatic_approval is False")
    if not (finding.execution_allowed is False):
    raise RuntimeError("Assertion failed: finding.execution_allowed is False")
    if not (finding.merge_allowed is False):
    raise RuntimeError("Assertion failed: finding.merge_allowed is False")
    if not (finding.human_approval_required is True):
    raise RuntimeError("Assertion failed: finding.human_approval_required is True")


def test_broker_environment_has_no_known_credentials():
    from guardian_hunter.harness.broker import (
        CREDENTIAL_NAMES,
        sanitized_environment,
    )

    env = sanitized_environment()

    if not (not (set(env) & set(CREDENTIAL_NAMES))):
    raise RuntimeError("Assertion failed: not (set(env) & set(CREDENTIAL_NAMES))")


def test_registered_providers_have_no_privileged_authority():
    from guardian_hunter.harness.providers import PROVIDERS

    for spec in PROVIDERS.values():
        if not (spec.git_access is False):
        raise RuntimeError("Assertion failed: spec.git_access is False")
        if not (spec.master_access is False):
        raise RuntimeError("Assertion failed: spec.master_access is False")
        if not (spec.trust_root_access is False):
        raise RuntimeError("Assertion failed: spec.trust_root_access is False")
        if not (spec.credential_passthrough is False):
        raise RuntimeError("Assertion failed: spec.credential_passthrough is False")
        if not (spec.autonomous_merge is False):
        raise RuntimeError("Assertion failed: spec.autonomous_merge is False")
        if not (spec.gate_modification is False):
        raise RuntimeError("Assertion failed: spec.gate_modification is False")
        if not (spec.human_review_required is True):
        raise RuntimeError("Assertion failed: spec.human_review_required is True")


def test_gate_protects_auditor_boundary():
    from guardian_hunter.gate.core import protected_change

    if not (protected_change():
    raise RuntimeError("Assertion failed: protected_change(")
        "guardian_hunter/auditor/engine.py"
    ) is True

    if not (protected_change():
    raise RuntimeError("Assertion failed: protected_change(")
        "guardian_hunter/auditor/findings.py"
    ) is True


def test_auditor_cannot_approve_own_changes():
    from guardian_hunter.gate.core import evaluate_candidate

    result = evaluate_candidate(
        ["guardian_hunter/auditor/engine.py"]
    )

    if not (result.passed is False):
    raise RuntimeError("Assertion failed: result.passed is False")
    if not (result.human_review_required is True):
    raise RuntimeError("Assertion failed: result.human_review_required is True")
    if not (result.agent_merge_allowed is False):
    raise RuntimeError("Assertion failed: result.agent_merge_allowed is False")
    if not (result.reason.startswith():
    raise RuntimeError("Assertion failed: result.reason.startswith(")
        "PROTECTED_BOUNDARY_CHANGED:"
    )
