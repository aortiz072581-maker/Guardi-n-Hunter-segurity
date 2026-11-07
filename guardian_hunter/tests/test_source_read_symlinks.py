import os

import pytest

from guardian_hunter.integration.codex_supervised import _safe_source_bytes


@pytest.fixture()
def project(tmp_path):
    root, outside = tmp_path / "project", tmp_path / "outside"
    (root / "src").mkdir(parents=True)
    (root / ".git").mkdir()
    outside.mkdir()
    (root / ".git" / "config").write_text("SECRETO-GIT")
    (root / "src" / "ok.py").write_text("print(1)")
    (outside / "secret.txt").write_text("SECRETO-FUERA")
    os.symlink(root / ".git", root / "alias_git")
    os.symlink(root / "src", root / "alias_src")
    os.symlink(outside, root / "dirlink")
    return root


def test_normal_file_is_readable(project):
    assert _safe_source_bytes(root=project, relative_path="src/ok.py") == b"print(1)"


@pytest.mark.parametrize("attack", [
    "alias_git/config",
    "alias_src/ok.py",
    "dirlink/secret.txt",
])
def test_source_read_rejects_symlink_components(project, attack):
    with pytest.raises(PermissionError, match="SYMLINK"):
        _safe_source_bytes(root=project, relative_path=attack)
