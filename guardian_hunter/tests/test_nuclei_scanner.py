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

    assert result["status"] == "blocked"
    assert result["authorized"] is False
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
    assert called["value"] is False


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

    assert len(findings) == 1
    assert findings[0]["category"] == "vulnerability"
    assert findings[0]["severity"] == "high"
    assert findings[0]["score"] == 75
    assert findings[0]["source"] == "nuclei"
    assert findings[0]["execution_allowed"] is False


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

    assert result["status"] == "ok"
    assert result["authorized"] is True
    assert len(result["findings"]) == 1
    assert result["findings"][0]["score"] == 95
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
