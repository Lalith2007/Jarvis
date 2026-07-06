"""Unit tests for the resolve-then-validate permission gate (env-driven roots)."""
from pathlib import Path

from app.config.settings import BASE_DIR
from app.security.permissions import permissions

REPO_ROOT = BASE_DIR.parent


def test_repo_root_allowed():
    assert permissions.allowed(str(BASE_DIR)) is True  # under the computed repo root


def test_path_inside_temp_allowed(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("hi")
    assert permissions.allowed(str(f)) is True
    assert permissions.resolve_if_allowed(str(f)) == f.resolve()


def test_home_root_denied():
    assert permissions.allowed(str(Path.home())) is False


def test_absolute_traversal_denied():
    assert permissions.allowed("/etc/passwd") is False


def test_relative_traversal_escape_denied():
    escape = str(REPO_ROOT / ".." / ".." / ".." / "etc" / "passwd")
    assert permissions.allowed(escape) is False
    assert permissions.resolve_if_allowed(escape) is None


def test_resolve_returns_resolved_path(tmp_path):
    (tmp_path / "b.txt").write_text("x")
    resolved = permissions.resolve_if_allowed(str(tmp_path / "a" / ".." / "b.txt"))
    assert resolved == (tmp_path / "b.txt").resolve()


def test_garbage_path_denied():
    assert permissions.allowed("\x00not-a-path") is False
