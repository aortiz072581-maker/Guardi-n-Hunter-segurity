from guardian_hunter.dashboard.diagnostic_cli import execute_diagnostic


def test_diagnostic_cli_blocks_unauthorized_target(
    monkeypatch,
    tmp_path,
):
    from guardian_hunter.dashboard import diagnostic_cli

    class FakeAssets:
        def is_authorized(self, target):
            return False

    class FakeEvidence:
        pass

    class FakePipeline:
        def __init__(self, asset_manager):
            self.asset_manager = asset_manager

    assets = FakeAssets()

    monkeypatch.setattr(
        diagnostic_cli,
        "AssetManager",
        lambda: assets,
    )
    monkeypatch.setattr(
        diagnostic_cli,
        "EvidenceStore",
        lambda path: FakeEvidence(),
    )
    monkeypatch.setattr(
        diagnostic_cli,
        "SecurityPipeline",
        FakePipeline,
    )

    result = execute_diagnostic("example.invalid")

    assert result["status"] == "blocked"
    assert result["execution_allowed"] is False
    assert result["response_locked"] is True
    assert result["reason"] == "TARGET_NOT_AUTHORIZED"
    assert result["diagnosis"] is None
