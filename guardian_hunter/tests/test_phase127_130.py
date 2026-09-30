"""Guardian Hunter — Phases 127 → 130 tests."""

from guardian_hunter.email.phase127_130 import (
    DRY_RUN,
    HUMAN_REVIEW_REQUIRED,
    READ_ONLY,
    REAL_EXECUTION_BLOCKED,
    RESPONSE_LOCKED,
    analyze_email_attachments,
)


def test_security_invariants():
    assert READ_ONLY is True
    assert DRY_RUN is True
    assert REAL_EXECUTION_BLOCKED is True
    assert HUMAN_REVIEW_REQUIRED is True
    assert RESPONSE_LOCKED is True


def test_safe_attachment():
    result = analyze_email_attachments([
        {
            "filename": "readme.txt",
            "content_type": "text/plain",
            "data": b"normal text",
        }
    ])

    assert result.analyzed is True
    assert result.blocked is False
    assert result.quarantine is False
    assert result.execution_allowed is False


def test_executable_is_blocked_and_quarantined():
    result = analyze_email_attachments([
        {
            "filename": "invoice.exe",
            "content_type": "application/octet-stream",
            "data": b"MZFAKE-STATIC-DATA",
        }
    ])

    assert result.blocked is True
    assert result.quarantine is True
    assert result.execution_allowed is False
    assert any(
        finding.category == "EXECUTABLE_CONTENT"
        for finding in result.findings
    )


def test_macro_document_is_blocked():
    result = analyze_email_attachments([
        {
            "filename": "document.xlsm",
            "content_type": "application/vnd.ms-excel.sheet.macroEnabled.12",
            "data": b"macro document",
        }
    ])

    assert result.blocked is True
    assert result.quarantine is True
    assert any(
        finding.category == "MACRO_ENABLED_DOCUMENT"
        for finding in result.findings
    )


def test_script_attachment_is_blocked():
    result = analyze_email_attachments([
        {
            "filename": "update.ps1",
            "content_type": "text/plain",
            "data": b"Write-Host test",
        }
    ])

    assert result.blocked is True
    assert result.execution_allowed is False
    assert any(
        finding.category == "SCRIPT_ATTACHMENT"
        for finding in result.findings
    )


def test_ioc_hash_match():
    data = b"known-test-sample"
    import hashlib

    digest = hashlib.sha256(data).hexdigest()

    result = analyze_email_attachments(
        [
            {
                "filename": "sample.bin",
                "content_type": "application/octet-stream",
                "data": data,
            }
        ],
        known_iocs={digest},
    )

    assert result.blocked is True
    assert digest in result.ioc_matches


def test_cve_matching_is_data_driven():
    result = analyze_email_attachments(
        [
            {
                "filename": "legacy.doc",
                "content_type": "application/msword",
                "data": b"legacy",
            }
        ],
        known_cves={"CVE-2026-12345"},
    )

    assert "CVE-2026-12345" in result.cve_matches
    assert result.blocked is True


def test_type_mismatch_detection():
    result = analyze_email_attachments([
        {
            "filename": "photo.exe",
            "content_type": "image/jpeg",
            "data": b"\xFF\xD8\xFFJPEG",
        }
    ])

    assert result.blocked is True
    assert any(
        finding.category == "TYPE_MISMATCH"
        for finding in result.findings
    )


def test_fail_closed():
    result = analyze_email_attachments([
        {
            "filename": "unknown.bin",
            "content_type": "application/octet-stream",
            "data": b"unknown",
        }
    ])

    assert result.execution_allowed is False
    assert result.response_locked is True
    assert result.human_review_required is True
