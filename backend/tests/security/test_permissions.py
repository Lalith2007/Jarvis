"""
Unit tests for the filesystem permission gate (resolve-then-validate).

Regression coverage for the path-traversal vulnerability where a lexical
prefix check on an unresolved path allowed `<root>/../../../etc/passwd` to
escape the sandbox.
"""
from pathlib import Path

from app.security.permissions import permissions


def test_allowed_root_itself():
    desktop = Path.home() / "Desktop"
    assert permissions.allowed(str(desktop)) is True


def test_path_inside_allowed_root(tmp_path):
    # tmp_path is under the system temp root, which is allowed.
    f = tmp_path / "x.txt"
    f.write_text("hi")
    assert permissions.allowed(str(f)) is True
    assert permissions.resolve_if_allowed(str(f)) == f.resolve()


def test_home_root_denied():
    # $HOME itself is not an allowed root (only Desktop/Documents/Downloads are).
    assert permissions.allowed(str(Path.home())) is False


def test_absolute_traversal_denied():
    assert permissions.allowed("/etc/passwd") is False


def test_relative_traversal_escape_denied():
    escape = str(Path.home() / "Desktop" / ".." / ".." / ".." / "etc" / "passwd")
    assert permissions.allowed(escape) is False
    assert permissions.resolve_if_allowed(escape) is None


def test_resolve_returns_resolved_path(tmp_path):
    # A path with a redundant segment inside an allowed root resolves cleanly.
    nested = tmp_path / "a" / ".." / "b.txt"
    (tmp_path / "b.txt").write_text("x")
    resolved = permissions.resolve_if_allowed(str(nested))
    assert resolved == (tmp_path / "b.txt").resolve()


def test_garbage_path_denied():
    assert permissions.allowed("\x00not-a-path") is False
