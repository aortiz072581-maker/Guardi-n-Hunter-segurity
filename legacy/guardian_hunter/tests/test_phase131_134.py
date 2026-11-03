"""Guardian Hunter — Phases 131 → 134 tests."""

from guardian_hunter.email.phase131_134 import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    build_defensive_response,
    export_evidence,
    security_digest,
)


def test_security_invariants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def test_critical_subject_is_logically_isolated():
    result = build_defensive_response(
        subject="attachment:invoice.exe",
        risk_level="CRITICAL",
        findings=[
            {
                "category": "EXECUTABLE_CONTENT",
                "severity": "CRITICAL",
            }
        ],
    )

    assert result.blocked is True
    assert result.isolation.isolation_requested is True
    assert result.isolation.isolation_active is True
    assert result.isolation.physical_action_performed is False
    assert result.execution_allowed is False
    assert result.response_state == "ISOLATED_REVIEW_REQUIRED"


def test_high_risk_requires_review():
    result = build_defensive_response(
        subject="attachment:macro.xlsm",
        risk_level="HIGH",
        findings=[
            {
                "category": "MACRO_ENABLED_DOCUMENT",
                "severity": "HIGH",
            }
        ],
    )

    assert result.blocked is True
    assert result.human_review_required is True
    assert result.response_locked is True
    assert result.execution_allowed is False


def test_clean_subject_is_not_isolated():
    result = build_defensive_response(
        subject="message:normal",
        risk_level="LOW",
        findings=[],
    )

    assert result.blocked is False
    assert result.isolation.isolation_active is False
    assert result.isolation.physical_action_performed is False
    assert result.execution_allowed is False
    assert result.response_state == "MONITORED"


def test_fail_closed_with_findings():
    result = build_defensive_response(
        subject="message:suspicious",
        risk_level="LOW",
        findings=[
            {
                "category": "SUSPICIOUS_INDICATOR",
                "severity": "MEDIUM",
            }
        ],
    )

    assert result.blocked is True
    assert result.isolation.isolation_active is True
    assert result.execution_allowed is False
    assert result.response_locked is True


def test_evidence_traceability():
    result = build_defensive_response(
        subject="attachment:test.exe",
        risk_level="CRITICAL",
        findings=[
            {
                "category": "EXECUTABLE_CONTENT",
                "severity": "CRITICAL",
            }
        ],
    )

    evidence = export_evidence(result)

    assert len(evidence) >= 3
    assert evidence[0]["event"] == "SECURITY_ASSESSMENT"
    assert any(
        item["event"] == "LOGICAL_ISOLATION"
        for item in evidence
    )
    assert any(
        item["event"] == "RESPONSE_BLOCKED"
        for item in evidence
    )


def test_evidence_digest_exists():
    result = build_defensive_response(
        subject="attachment:test.exe",
        risk_level="HIGH",
        findings=[
            {
                "category": "DANGEROUS_EXTENSION",
                "severity": "HIGH",
            }
        ],
    )

    digest = security_digest(result)

    assert isinstance(digest, str)
    assert len(digest) == 64


def test_physical_action_never_performed():
    result = build_defensive_response(
        subject="attachment:malware.exe",
        risk_level="CRITICAL",
        findings=[
            {
                "category": "KNOWN_IOC",
                "severity": "CRITICAL",
            }
        ],
    )

    assert result.isolation.physical_action_performed is False
    assert result.execution_allowed is False
    assert REAL_EXECUTION_BLOCKED is True
