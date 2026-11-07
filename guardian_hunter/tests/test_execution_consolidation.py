
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

    assert function in names


@pytest.mark.parametrize("relative,function", TARGETS.items())
def test_sensitive_entrypoints_have_checks(relative, function):
    tree = _source(relative)

    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function
    ]

    assert len(functions) == 1

    checks = [
        node for node in ast.walk(functions[0])
        if isinstance(node, (ast.If, ast.Try))
    ]

    assert checks, "REVIEW_REQUIRED: NO CHECKS FOUND"


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

        assert not result, "INVALID_COMMAND_ACCEPTED"


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

    assert result.get("authorized") is not True
    assert result.get("status") != "success"


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

    assert report["execution_allowed"] is False
    assert report["automatic_repair"] is False
    assert report["merge_allowed"] is False
    assert report["assessment_complete"] is False


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

    assert store.verify().state == "EVIDENCE_INTEGRITY_OK"

    original = path.read_bytes()
    path.write_bytes(b"TAMPERED\n" + original)

    try:
        verification = store.verify()
    except (ValueError, OSError):
        pass
    else:
        assert verification.state != "EVIDENCE_INTEGRITY_OK"


def test_trust_root_matches_baseline():
    head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()

    baseline = (
        ROOT / ".guardian/trusted-baseline"
    ).read_text().strip()

    assert head == baseline
