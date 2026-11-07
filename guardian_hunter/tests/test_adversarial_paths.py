import os

import pytest

from guardian_hunter.agent.adapter import resolve_in_workspace, validate_relative_path
from guardian_hunter.repair.executor import _resolve_target

pytestmark = pytest.mark.skipif(not hasattr(os, "symlink"), reason="requiere symlinks")


@pytest.fixture()
def arena(tmp_path):
    ws, outside = tmp_path / "workspace", tmp_path / "outside"
    (ws / "src").mkdir(parents=True)
    (ws / ".git").mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("TOP-SECRET")
    (ws / "src" / "ok.py").write_text("print('ok')")
    os.symlink(outside, ws / "dirlink")
    os.symlink(outside / "secret.txt", ws / "filelink")
    os.symlink(outside / "nuevo.txt", ws / "dangling")
    os.symlink("../../outside", ws / "src" / "relative")
    os.symlink(ws / ".git", ws / "alias_git")
    os.symlink(ws / "src", ws / "alias_src")
    return ws


def test_legitimate_path_is_allowed(arena):
    assert resolve_in_workspace(arena, "src/ok.py") == (arena / "src" / "ok.py").resolve()


@pytest.mark.parametrize("attack,code", [
    ("dirlink/secret.txt", "SYMLINK_FORBIDDEN"),
    ("filelink", "SYMLINK_FORBIDDEN"),
    ("dangling", "SYMLINK_FORBIDDEN"),
    ("src/relative/secret.txt", "SYMLINK_FORBIDDEN"),
    ("alias_git/config", "SYMLINK_FORBIDDEN"),
    ("alias_src/ok.py", "SYMLINK_FORBIDDEN"),
    ("../outside/secret.txt", "PATH_TRAVERSAL_FORBIDDEN"),
    ("src/../../outside", "PATH_TRAVERSAL_FORBIDDEN"),
    ("/etc/passwd", "ABSOLUTE_PATH_FORBIDDEN"),
    ("src/ok.py\x00.txt", "NULL_BYTE_FORBIDDEN"),
    (".git/config", "FORBIDDEN_PATH"),
    ("", "EMPTY_PATH"),
])
def test_adapter_rejects_escape_attempts(arena, attack, code):
    with pytest.raises(ValueError, match=code):
        resolve_in_workspace(arena, attack)


@pytest.mark.parametrize("attack", ["dirlink/secret.txt", "filelink", "src/relative/secret.txt"])
def test_executor_rejects_symlink_escapes(arena, attack):
    with pytest.raises(RuntimeError, match="SYMLINK"):
        _resolve_target(arena, attack)


def test_characterization_lexical_validator_alone_misses_symlinks(arena):
    assert validate_relative_path("dirlink/secret.txt")
    assert validate_relative_path("alias_git/config")
