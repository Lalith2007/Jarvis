"""Regression tests for resolve-then-validate permission gate (path traversal)."""
from pathlib import Path

from app.config.settings import BASE_DIR
from app.security.permissions import permissions
from app.tools import tool_registry
from app.tools.models import ToolCall

REPO_ROOT = BASE_DIR.parent


def test_traversal_escape_denied():
    escape = str(REPO_ROOT / ".." / ".." / ".." / "etc" / "passwd")
    assert permissions.allowed(escape) is False
    assert permissions.resolve_if_allowed(escape) is None


def test_read_traversal_denied():
    result = tool_registry.execute(ToolCall(
        name="read_file",
        arguments={"path": str(REPO_ROOT / ".." / ".." / ".." / "etc" / "passwd")}))
    assert not result.success
    assert result.output == "Access denied."


def test_write_traversal_denied():
    etc_target = str(REPO_ROOT / ".." / ".." / ".." / "etc" / "jarvis.txt")
    denied = tool_registry.execute(ToolCall(name="write_file", arguments={"path": etc_target, "content": "x"}))
    assert not denied.success
    assert denied.output == "Access denied."


def test_allowed_path_within_root(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hi")
    result = tool_registry.execute(ToolCall(name="read_file", arguments={"path": str(f)}))
    assert result.success
    assert result.output == "hi"
