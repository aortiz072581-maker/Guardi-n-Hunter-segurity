
import subprocess
import time
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from guardian_hunter.runner.agent_runner import validate_command
from guardian_hunter.modules.nuclei_scanner import run_nuclei_authorized
from guardian_hunter.integration.security_sensor_adapter import assess_security_sensors
from guardian_hunter.evidence.persistence import EvidenceStore


@pytest.mark.parametrize("command", [
    None, "", 123, {}, ["python", None]
])
def test_invalid_commands_rejected(command):
    with pytest.raises((RuntimeError, TypeError, ValueError, PermissionError)):
        validate_command(command)


def test_unauthorized_nuclei_target_never_executes():
    class DeniedAssets:
        def is_authorized(self, *args, **kwargs):
            return False

    with patch("subprocess.run") as process:
        result = run_nuclei_authorized(
            "https://unauthorized.invalid",
            asset_manager=DeniedAssets(),
        )
        if not (result["authorized"] is False):
        raise RuntimeError("Assertion failed: result["authorized"] is False")
        process.assert_not_called()


def test_missing_sensor_tools_fail_closed(tmp_path):
    with patch("subprocess.run", side_effect=OSError("MISSING_BINARY")):
        result = assess_security_sensors(
            tmp_path,
            gitleaks_binary=tmp_path / "missing-gitleaks",
            osv_binary=tmp_path / "missing-osv",
        )
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (():
    raise RuntimeError("Assertion failed: (")
        result.get("assessment_complete") is False
        or "ERROR" in str(result.get("states"))
    )


def test_evidence_tampering_detected(tmp_path):
    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path)

    store.append(
        evidence_id=str(uuid.uuid4()),
        event_type="FINAL_SECURITY_AUDIT",
        timestamp=time.time(),
        payload={
            "execution_allowed": False,
            "automatic_repair": False,
            "merge_allowed": False,
        },
    )

    if not (store.verify().state == "EVIDENCE_INTEGRITY_OK"):
    raise RuntimeError("Assertion failed: store.verify().state == "EVIDENCE_INTEGRITY_OK"")

    path.write_bytes(b"TAMPERED\\n" + path.read_bytes())

    try:
        result = store.verify()
    except (ValueError, OSError):
        pass
    else:
        if not (result.state != "EVIDENCE_INTEGRITY_OK"):
        raise RuntimeError("Assertion failed: result.state != "EVIDENCE_INTEGRITY_OK"")


@pytest.mark.parametrize("component,function", [
    ("runner/agent_runner.py", "run_candidate"),
    ("runner/proot_runner.py", "main"),
    ("integration/codex_supervised.py", "prepare_codex_candidate"),
    ("modules/nuclei_scanner.py", "run_nuclei_authorized"),
    ("integration/security_sensor_adapter.py", "assess_security_sensors"),
])
def test_execution_entrypoints_present(component, function):
    import ast

    path = Path("guardian_hunter") / component
    tree = ast.parse(path.read_text())

    if not (any():
    raise RuntimeError("Assertion failed: any(")
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function
        for node in tree.body
    )


def test_central_security_verifier():
    from guardian_hunter.security.security_verifier import (
        run_security_verification,
        final_verdict,
    )

    if not (final_verdict(run_security_verification())):
    raise RuntimeError("Assertion failed: final_verdict(run_security_verification())")
