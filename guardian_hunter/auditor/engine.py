"""Deterministic read-only security auditor for Guardian Hunter.

This engine observes security policy and reports inconsistencies.
It has no repair, approval, execution, merge, or write authority.
"""

from __future__ import annotations

from guardian_hunter.auditor.findings import (
    Confidence,
    Finding,
    Severity,
    validate_findings,
)
from guardian_hunter.containment.ai_policy import (
    DENIED_PREFIXES as CONTAINMENT_PREFIXES,
    POLICY,
    validate_policy,
)
from guardian_hunter.gate.core import (
    AGENT_MERGE_ALLOWED,
    FAIL_CLOSED,
    HUMAN_REVIEW_REQUIRED,
    PROTECTED_PREFIXES as GATE_PREFIXES,
)
from guardian_hunter.harness.launcher import (
    DENIED_PREFIXES as HARNESS_PREFIXES,
)
from guardian_hunter.harness.providers import (
    PROVIDERS,
    validate_provider,
)


AUDITOR_READ_ONLY = True
AUTOMATIC_REPAIR = False
AUTOMATIC_APPROVAL = False
EXECUTION_ALLOWED = False
MERGE_ALLOWED = False
HUMAN_APPROVAL_REQUIRED = True


def _normalize_prefix(value: object) -> str:
    return str(value).replace("\\", "/").strip("/") + "/"


def _prefixes(values: object) -> frozenset[str]:
    return frozenset(
        _normalize_prefix(value)
        for value in values
    )


def audit_security_boundaries() -> tuple[Finding, ...]:
    """Compare independent security boundaries without changing them."""

    findings: list[Finding] = []

    containment = _prefixes(CONTAINMENT_PREFIXES)
    harness = _prefixes(HARNESS_PREFIXES)
    gate = _prefixes(GATE_PREFIXES)

    # Containment and harness are expected to agree on provider-denied
    # security boundaries. Any divergence can create policy confusion.
    if containment != harness:
        only_containment = sorted(containment - harness)
        only_harness = sorted(harness - containment)

        findings.append(
            Finding(
                finding_id="GH-001",
                severity=Severity.HIGH,
                confidence=Confidence.CONFIRMED,
                title="Containment and harness protected paths diverge",
                description=(
                    "The external-provider containment policy and "
                    "harness launcher do not protect the same path set."
                ),
                risk=(
                    "Independent policy layers can disagree about "
                    "whether an AI provider may access a security path."
                ),
                evidence=(
                    f"containment_only={only_containment}",
                    f"harness_only={only_harness}",
                ),
                affected_files=(
                    "guardian_hunter/containment/ai_policy.py",
                    "guardian_hunter/harness/launcher.py",
                ),
                proposed_fix=(
                    "Centralize or mechanically derive the shared "
                    "provider protected-path policy after human review."
                ),
                required_tests=(
                    "test_containment_and_harness_paths_match",
                    "test_protected_paths_fail_closed",
                ),
            )
        )

    # The promotion Gate may intentionally protect more paths than the
    # provider boundary. It must not protect fewer overlapping trust paths.
    required_gate = frozenset({
        "guardian_hunter/gate/",
        "guardian_hunter/governance/",
    })

    missing_gate = sorted(required_gate - gate)

    if missing_gate:
        findings.append(
            Finding(
                finding_id="GH-002",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="Guardian Gate omits required trust boundaries",
                description=(
                    "The promotion Gate does not include every required "
                    "trust-boundary path."
                ),
                risk=(
                    "A candidate could alter a required trust boundary "
                    "without the Gate classifying it as protected."
                ),
                evidence=(
                    f"missing_gate_prefixes={missing_gate}",
                ),
                affected_files=(
                    "guardian_hunter/gate/core.py",
                ),
                proposed_fix=(
                    "Add the missing trust boundaries only after "
                    "reinforced human authorization."
                ),
                required_tests=(
                    "test_gate_covers_required_trust_boundaries",
                ),
            )
        )

    if not validate_policy():
        findings.append(
            Finding(
                finding_id="GH-003",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="AI containment policy invariant failed",
                description=(
                    "The active AI containment policy no longer "
                    "satisfies its fail-closed invariant."
                ),
                risk=(
                    "An external provider could receive authority that "
                    "Guardian Hunter is designed to deny."
                ),
                evidence=("validate_policy=False",),
                affected_files=(
                    "guardian_hunter/containment/ai_policy.py",
                ),
                proposed_fix=(
                    "Restore the fail-closed policy after reinforced "
                    "human review."
                ),
                required_tests=(
                    "test_ai_policy_remains_fail_closed",
                ),
            )
        )

    authority_errors: list[str] = []

    if AGENT_MERGE_ALLOWED:
        authority_errors.append("AGENT_MERGE_ALLOWED=True")

    if not FAIL_CLOSED:
        authority_errors.append("FAIL_CLOSED=False")

    if not HUMAN_REVIEW_REQUIRED:
        authority_errors.append("HUMAN_REVIEW_REQUIRED=False")

    if authority_errors:
        findings.append(
            Finding(
                finding_id="GH-004",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="Guardian Gate authority invariant failed",
                description=(
                    "One or more Gate authority controls are unsafe."
                ),
                risk=(
                    "The promotion boundary could cease to require "
                    "fail-closed human-controlled review."
                ),
                evidence=tuple(authority_errors),
                affected_files=(
                    "guardian_hunter/gate/core.py",
                ),
                proposed_fix=(
                    "Restore Gate authority invariants after reinforced "
                    "human authorization."
                ),
                required_tests=(
                    "test_gate_authority_is_fail_closed",
                ),
            )
        )

    provider_errors: list[str] = []

    for provider, spec in PROVIDERS.items():
        try:
            validate_provider(spec)
        except PermissionError as exc:
            provider_errors.append(
                f"{provider.value}:{exc}"
            )

    if provider_errors:
        findings.append(
            Finding(
                finding_id="GH-005",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="External provider authority invariant failed",
                description=(
                    "At least one registered AI provider violates "
                    "the required provider security contract."
                ),
                risk=(
                    "A provider could receive Git, credential, trust-root, "
                    "merge, or gate-modification authority."
                ),
                evidence=tuple(provider_errors),
                affected_files=(
                    "guardian_hunter/harness/providers.py",
                ),
                proposed_fix=(
                    "Restore the provider contract before any provider "
                    "execution is enabled."
                ),
                required_tests=(
                    "test_all_provider_contracts_fail_closed",
                ),
            )
        )

    result = tuple(findings)
    validate_findings(result)
    return result


def audit() -> tuple[Finding, ...]:
    if not AUDITOR_READ_ONLY:
        raise PermissionError("AUDITOR_READ_ONLY_REQUIRED")

    if AUTOMATIC_REPAIR:
        raise PermissionError("AUTOMATIC_REPAIR_FORBIDDEN")

    if AUTOMATIC_APPROVAL:
        raise PermissionError("AUTOMATIC_APPROVAL_FORBIDDEN")

    if EXECUTION_ALLOWED:
        raise PermissionError("AUDITOR_EXECUTION_FORBIDDEN")

    if MERGE_ALLOWED:
        raise PermissionError("AUDITOR_MERGE_FORBIDDEN")

    if not HUMAN_APPROVAL_REQUIRED:
        raise PermissionError("HUMAN_APPROVAL_REQUIRED")

    return audit_extended_security()


def audit_extended_security() -> tuple[Finding, ...]:
    """Audit authority, credentials, provider contracts and trust coverage."""

    findings = list(audit_security_boundaries())
    existing_ids = {item.finding_id for item in findings}

    # The supervised auditor influences security conclusions.
    # Report if the Gate does not explicitly protect it.
    gate = _prefixes(GATE_PREFIXES)
    auditor_boundary = "guardian_hunter/auditor/"

    if auditor_boundary not in gate and "GH-006" not in existing_ids:
        findings.append(
            Finding(
                finding_id="GH-006",
                severity=Severity.HIGH,
                confidence=Confidence.CONFIRMED,
                title="Supervised auditor is outside Gate protected boundary",
                description=(
                    "Guardian's supervised security auditor can influence "
                    "security findings but is not explicitly classified as "
                    "a protected Gate path."
                ),
                risk=(
                    "A candidate modification to auditor logic could be "
                    "classified as ordinary code instead of a trust-boundary "
                    "change."
                ),
                evidence=(
                    f"auditor_boundary={auditor_boundary}",
                    f"gate_prefixes={sorted(gate)}",
                ),
                affected_files=(
                    "guardian_hunter/gate/core.py",
                    "guardian_hunter/auditor/engine.py",
                ),
                proposed_fix=(
                    "Consider adding guardian_hunter/auditor/ to the Gate "
                    "protected boundary after reinforced human review."
                ),
                required_tests=(
                    "test_gate_protects_auditor_boundary",
                    "test_auditor_cannot_approve_own_changes",
                ),
            )
        )

    # Broker credentials must never be present in its sanitized environment.
    from guardian_hunter.harness.broker import (
        CREDENTIAL_NAMES,
        environment_is_sanitized,
        sanitized_environment,
    )

    broker_env = sanitized_environment()

    leaked = sorted(
        name for name in CREDENTIAL_NAMES
        if name in broker_env
    )

    if (
        leaked
        or not environment_is_sanitized(broker_env)
    ) and "GH-007" not in existing_ids:
        findings.append(
            Finding(
                finding_id="GH-007",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="Broker sanitized environment exposes credentials",
                description=(
                    "The environment prepared for an external provider "
                    "contains credential-bearing variables."
                ),
                risk=(
                    "An external AI provider could receive host credentials."
                ),
                evidence=(
                    f"credential_variables={leaked}",
                ),
                affected_files=(
                    "guardian_hunter/harness/broker.py",
                ),
                proposed_fix=(
                    "Restore strict credential removal before provider "
                    "execution can ever be enabled."
                ),
                required_tests=(
                    "test_broker_environment_contains_no_credentials",
                ),
            )
        )

    # Every provider must remain incapable of receiving privileged authority.
    provider_authority: list[str] = []

    for provider, spec in PROVIDERS.items():
        unsafe = []

        if spec.git_access:
            unsafe.append("git_access")
        if spec.master_access:
            unsafe.append("master_access")
        if spec.trust_root_access:
            unsafe.append("trust_root_access")
        if spec.credential_passthrough:
            unsafe.append("credential_passthrough")
        if spec.autonomous_merge:
            unsafe.append("autonomous_merge")
        if spec.gate_modification:
            unsafe.append("gate_modification")
        if not spec.human_review_required:
            unsafe.append("human_review_disabled")

        if unsafe:
            provider_authority.append(
                f"{provider.value}:{','.join(unsafe)}"
            )

    if provider_authority and "GH-008" not in existing_ids:
        findings.append(
            Finding(
                finding_id="GH-008",
                severity=Severity.CRITICAL,
                confidence=Confidence.CONFIRMED,
                title="Provider has forbidden authority",
                description=(
                    "At least one AI provider has privileged authority "
                    "that violates Guardian's external-agent model."
                ),
                risk=(
                    "The provider could cross the human-controlled "
                    "security boundary."
                ),
                evidence=tuple(provider_authority),
                affected_files=(
                    "guardian_hunter/harness/providers.py",
                ),
                proposed_fix=(
                    "Remove forbidden provider authority before execution."
                ),
                required_tests=(
                    "test_provider_has_no_privileged_authority",
                ),
            )
        )

    result = tuple(findings)
    validate_findings(result)
    return result
