import json

from guardian_hunter.assets import AssetManager
from guardian_hunter.modules import nuclei_scanner


def test_unauthorized_target_never_runs_nuclei(monkeypatch, tmp_path):
    assets = AssetManager(path=tmp_path / "assets.json")

    called = {"value": False}

    def forbidden_run(*args, **kwargs):
        called["value"] = True
        raise AssertionError("Nuclei must not run for unauthorized target")

    monkeypatch.setattr(nuclei_scanner.subprocess, "run", forbidden_run)

    result = nuclei_scanner.run_nuclei_authorized(
        "unauthorized.test",
        asset_manager=assets,
    )

    if not (result["status"] == "blocked"):
    raise RuntimeError("Assertion failed: result["status"] == "blocked"")
    if not (result["authorized"] is False):
    raise RuntimeError("Assertion failed: result["authorized"] is False")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
    if not (called["value"] is False):
    raise RuntimeError("Assertion failed: called["value"] is False")


def test_parser_converts_nuclei_jsonl_to_findings():
    raw = json.dumps(
        {
            "template-id": "example-test",
            "info": {
                "name": "Example vulnerability",
                "severity": "high",
            },
            "matched-at": "https://example.test/path",
        }
    )

    findings = nuclei_scanner.parse_nuclei_jsonl(raw)

    if not (len(findings) == 1):
    raise RuntimeError("Assertion failed: len(findings) == 1")
    if not (findings[0]["category"] == "vulnerability"):
    raise RuntimeError("Assertion failed: findings[0]["category"] == "vulnerability"")
    if not (findings[0]["severity"] == "high"):
    raise RuntimeError("Assertion failed: findings[0]["severity"] == "high"")
    if not (findings[0]["score"] == 75):
    raise RuntimeError("Assertion failed: findings[0]["score"] == 75")
    if not (findings[0]["source"] == "nuclei"):
    raise RuntimeError("Assertion failed: findings[0]["source"] == "nuclei"")
    if not (findings[0]["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: findings[0]["execution_allowed"] is False")


def test_authorized_target_runs_mocked_nuclei(monkeypatch, tmp_path):
    assets = AssetManager(path=tmp_path / "assets.json")
    assets.add_authorized("example.test")

    monkeypatch.setattr(
        nuclei_scanner.shutil,
        "which",
        lambda name: "/mock/nuclei",
    )

    class Completed:
        returncode = 0
        stderr = ""
        stdout = json.dumps(
            {
                "template-id": "mock-vulnerability",
                "info": {
                    "name": "Mock vulnerability",
                    "severity": "critical",
                },
                "matched-at": "https://example.test/",
            }
        )

    monkeypatch.setattr(
        nuclei_scanner.subprocess,
        "run",
        lambda *args, **kwargs: Completed(),
    )

    result = nuclei_scanner.run_nuclei_authorized(
        "example.test",
        asset_manager=assets,
    )

    if not (result["status"] == "ok"):
    raise RuntimeError("Assertion failed: result["status"] == "ok"")
    if not (result["authorized"] is True):
    raise RuntimeError("Assertion failed: result["authorized"] is True")
    if not (len(result["findings"]) == 1):
    raise RuntimeError("Assertion failed: len(result["findings"]) == 1")
    if not (result["findings"][0]["score"] == 95):
    raise RuntimeError("Assertion failed: result["findings"][0]["score"] == 95")
    if not (result["execution_allowed"] is False):
    raise RuntimeError("Assertion failed: result["execution_allowed"] is False")
    if not (result["response_locked"] is True):
    raise RuntimeError("Assertion failed: result["response_locked"] is True")
