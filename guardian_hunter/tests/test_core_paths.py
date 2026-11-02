import pytest

from guardian_hunter.core.paths import normalize_relative
from guardian_hunter.integration.codex_supervised import _normalize_relative_path
from guardian_hunter.repair.executor import _normalize_relative

VALID = ["a.py", "src/ok.py", "a/b/c.txt", "ünï/ñ.py", "a\\b.py", "a b/c.py"]

HOSTILE = [
    ("../x", "PATH_TRAVERSAL_FORBIDDEN"),
    ("a/../b", "PATH_TRAVERSAL_FORBIDDEN"),
    ("a\\..\\b", "PATH_TRAVERSAL_FORBIDDEN"),
    ("/etc/passwd", "ABSOLUTE_PATH_FORBIDDEN"),
    ("\\etc\\passwd", "ABSOLUTE_PATH_FORBIDDEN"),
    ("C:/x", "ABSOLUTE_PATH_FORBIDDEN"),
    ("C:\\x", "ABSOLUTE_PATH_FORBIDDEN"),
    ("", "INVALID_PATH"),
    ("a\x00b", "INVALID_PATH"),
    ("a\nb", "INVALID_PATH"),
    ("a\tb", "INVALID_PATH"),
    ("a//b", "INVALID_PATH"),
    ("./a", "INVALID_PATH"),
    ("a/./b", "INVALID_PATH"),
    ("a/", "INVALID_PATH"),
    ("x" * 2000, "INVALID_PATH"),
]

CORPUS = VALID + [h[0] for h in HOSTILE] + ["...", "a/.../b", "~/x", "%2e%2e/x", " a", "a /b"]


@pytest.mark.parametrize("value", VALID)
def test_valid_paths_are_accepted(value):
    assert normalize_relative(value) == value.replace("\\", "/")


@pytest.mark.parametrize("value,code", HOSTILE)
def test_hostile_paths_are_rejected_with_exact_code(value, code):
    with pytest.raises(ValueError, match=code):
        normalize_relative(value)


def test_non_string_is_rejected():
    with pytest.raises(TypeError, match="PATH_MUST_BE_STRING"):
        normalize_relative(None)


def _rejects(fn, value):
    try:
        fn(value)
    except Exception:
        return True
    return False


@pytest.mark.parametrize("value", CORPUS)
def test_new_validator_is_at_least_as_strict_as_both_old_ones(value):
    """Garantia de migracion: lo que cualquiera de los viejos rechaza, el nuevo tambien."""
    if _rejects(_normalize_relative, value) or _rejects(_normalize_relative_path, value):
        assert _rejects(normalize_relative, value)
