from guardian_hunter.release.phase171 import validate_release_candidate
from guardian_hunter.release.phase172 import validate_demo
from guardian_hunter.release.phase173 import validate_evidence_package
from guardian_hunter.release.phase174 import validate_security_assertions
from guardian_hunter.release.phase175 import validate_release_manifest
from guardian_hunter.release.phase176 import validate_integrity_manifest
from guardian_hunter.release.phase177 import validate_evaluation_boundary
from guardian_hunter.release.phase178 import run_final_regression
from guardian_hunter.release.phase179 import run_release_gate
from guardian_hunter.release.phase180 import build_master_release_attestation


def test_phase171():
    assert validate_release_candidate() is True


def test_phase172():
    result = validate_demo()
    assert result["action"] == "NO_REAL_EXECUTION"
    assert result["locked"] is True


def test_phase173():
    assert validate_evidence_package() is True


def test_phase174():
    assert validate_security_assertions() is True


def test_phase175():
    assert validate_release_manifest() is True


def test_phase176():
    assert validate_integrity_manifest() is True


def test_phase177():
    assert validate_evaluation_boundary() is True


def test_phase178():
    result = run_final_regression()
    assert result["passed"] is True
    assert result["checks"] == result["passed_checks"]


def test_phase179():
    result = run_release_gate()

    assert result["release_candidate_ready"] is True
    assert result["score"] == 100
    assert result["release_allowed"] is False
    assert result["READ_ONLY"] is True
    assert result["DRY_RUN"] is True
    assert result["REAL_EXECUTION_BLOCKED"] is True
    assert result["HUMAN_REVIEW_REQUIRED"] is True
    assert result["RESPONSE_LOCKED"] is True


def test_phase180():
    result = build_master_release_attestation()

    assert result["state"] == "RELEASE_CANDIDATE_READY"
    assert result["score"] == 100
    assert result["release_allowed"] is False
    assert result["READ_ONLY"] is True
    assert result["DRY_RUN"] is True
    assert result["REAL_EXECUTION_BLOCKED"] is True
    assert result["HUMAN_REVIEW_REQUIRED"] is True
    assert result["RESPONSE_LOCKED"] is True
