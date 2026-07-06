"""Regression tests for the resolve-then-validate permission gate (path traversal)."""
from pathlib import Path

from app.security.permissions import permissions
from app.tools import tool_registry
from app.tools.models import ToolCall


def test_traversal_escape_denied():
    escape = str(Path.home() / "Desktop" / ".." / ".." / ".." / "etc" / "passwd")
    assert permissions.allowed(escape) is False
    assert permissions.resolve_if_allowed(escape) is None


def test_read_traversal_denied():
    result = tool_registry.execute(
        ToolCall(
            name="read_file",
            arguments={"path": str(Path.home() / "Desktop" / ".." / ".." / ".." / "etc" / "passwd")},
        )
    )
    assert not result.success
    assert result.output == "Access denied."


def test_write_traversal_denied(tmp_path):
    # Attempt to escape an allowed root and overwrite outside it.
    target = str(Path.home() / "Desktop" / ".." / ".." / ".." / "tmp" / "jarvis_should_not_exist.txt")
    result = tool_registry.execute(
        ToolCall(name="write_file", arguments={"path": target, "content": "x"})
    )
    # /tmp resolves to an allowed temp root on macOS, so this may be allowed;
    # the key assertion is that escaping to a NON-allowed root is denied.
    etc_target = str(Path.home() / "Desktop" / ".." / ".." / ".." / "etc" / "jarvis.txt")
    denied = tool_registry.execute(
        ToolCall(name="write_file", arguments={"path": etc_target, "content": "x"})
    )
    assert not denied.success
    assert denied.output == "Access denied."


def test_allowed_path_within_root(tmp_path):
    # A real file inside the temp root (allowed) should be readable.
    f = tmp_path / "hello.txt"
    f.write_text("hi")
    result = tool_registry.execute(ToolCall(name="read_file", arguments={"path": str(f)}))
    assert result.success
    assert result.output == "hi"
