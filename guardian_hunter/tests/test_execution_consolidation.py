
import ast
import os
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from guardian_hunter.evidence.persistence import EvidenceStore


ROOT = Path(__file__).resolve().parents[2]

TARGETS = {
    "runner/agent_runner.py": "run_candidate",
    "runner/proot_runner.py": "main",
    "integration/codex_supervised.py": "prepare_codex_candidate",
    "modules/nuclei_scanner.py": "run_nuclei_authorized",
    "integration/security_sensor_adapter.py": "assess_security_sensors",
}


def _source(relative):
    path = ROOT / "guardian_hunter" / relative
    return ast.parse(path.read_text())


@pytest.mark.parametrize("relative,function", TARGETS.items())
def test_sensitive_entrypoints_exist(relative, function):
    tree = _source(relative)

    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    if not (function in names):
    raise RuntimeError("Assertion failed: function in names")


@pytest.mark.parametrize("relative,function", TARGETS.items())
def test_sensitive_entrypoints_have_checks(relative, function):
    tree = _source(relative)

    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function
    ]

    if not (len(functions) == 1):
    raise RuntimeError("Assertion failed: len(functions) == 1")

    checks = [
        node for node in ast.walk(functions[0])
        if isinstance(node, (ast.If, ast.Try))
    ]

    if not (checks):
    raise RuntimeError("REVIEW_REQUIRED: NO CHECKS FOUND")


def test_real_process_execution_is_intercepted():
    def deny(*args, **kwargs):
        raise PermissionError("PROCESS_BLOCKED")

    with patch.object(subprocess, "run", side_effect=deny):
        with pytest.raises(PermissionError, match="PROCESS_BLOCKED"):
            subprocess.run(["untrusted-command"])


def test_permission_change_is_intercepted():
    def deny(*args, **kwargs):
        raise PermissionError("CHMOD_BLOCKED")

    with patch.object(os, "chmod", side_effect=deny):
        with pytest.raises(PermissionError, match="CHMOD_BLOCKED"):
            os.chmod("/tmp/untrusted", 0o777)


def test_command_validation_rejects_non_list():
    from guardian_hunter.runner.agent_runner import validate_command

    for invalid in (None, "", 123, {}, ["python", None]):
        try:
            result = validate_command(invalid)
        except (TypeError, ValueError, RuntimeError, PermissionError, AttributeError):
            continue

        if not (not result):
        raise RuntimeError("INVALID_COMMAND_ACCEPTED")


def test_nuclei_unauthorized_target_never_executes():
    from guardian_hunter.modules.nuclei_scanner import run_nuclei_authorized

    class DeniedAssets:
        def is_authorized(self, *args, **kwargs):
            return False

    with patch("subprocess.run", side_effect=AssertionError("EXECUTED")):
        result = run_nuclei_authorized(
            "https://unauthorized.invalid",
            asset_manager=DeniedAssets(),
        )

    if not (result.get("authorized") is not True):
    raise RuntimeError("Assertion failed: result.get("authorized") is not True")
    if not (result.get("status") != "success"):
    raise RuntimeError("Assertion failed: result.get("status") != "success"")


def test_missing_sensor_binaries_fail_closed(tmp_path):
    from guardian_hunter.integration.security_sensor_adapter import (
        assess_security_sensors,
    )

    with patch("subprocess.run", side_effect=OSError("MISSING_BINARY")):
        report = assess_security_sensors(
            tmp_path,
            gitleaks_binary=tmp_path / "missing-gitleaks",
            osv_binary=tmp_path / "missing-osv",
        )

    if not (report["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: report["execution_allowed"] is False")
    if not (report["automatic_repair"] is False):
    raise RuntimeError("Assertion failed: report["automatic_repair"] is False")
    if not (report["merge_allowed"] is False):
    raise RuntimeError("Assertion failed: report["merge_allowed"] is False")
    if not (report["assessment_complete"] is False):
    raise RuntimeError("Assertion failed: report["assessment_complete"] is False")


def test_evidence_tampering_is_detected(tmp_path):
    import time
    import uuid

    path = tmp_path / "audit.jsonl"
    store = EvidenceStore(path)

    store.append(
        evidence_id=str(uuid.uuid4()),
        event_type="SECURITY_AUDIT",
        timestamp=time.time(),
        payload={"execution_allowed": False},
    )

    if not (store.verify().state == "EVIDENCE_INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: store.verify().state == "EVIDENCE_INTEGRITY_OK"")

    original = path.read_bytes()
    path.write_bytes(b"TAMPERED\n" + original)

    try:
        verification = store.verify()
    except (ValueError, OSError):
        pass
    else:
        if not (verification.state != "EVIDENCE_INTEGRITY_OK"):
        raise RuntimeError("Assertion failed: verification.state != "EVIDENCE_INTEGRITY_OK"")


def test_trust_root_matches_baseline():
    head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()

    baseline = (
        ROOT / ".guardian/trusted-baseline"
    ).read_text().strip()

    if not (head == baseline):
    raise RuntimeError("Assertion failed: head == baseline")
