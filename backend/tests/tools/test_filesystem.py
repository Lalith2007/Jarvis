from pathlib import Path

from app.tools import tool_registry
from app.tools.models import ToolCall


def test_list_directory_allowed():
    # Desktop is an allowed root.
    result = tool_registry.execute(
        ToolCall(
            name="list_directory",
            arguments={"path": str(Path.home() / "Desktop")},
        )
    )
    assert result.success
    assert len(result.output) >= 0


def test_list_directory_denied_home():
    # $HOME itself is NOT an allowed root — must be denied.
    result = tool_registry.execute(
        ToolCall(
            name="list_directory",
            arguments={"path": str(Path.home())},
        )
    )
    assert not result.success
    assert result.output == "Access denied."


def test_list_directory_denied_traversal():
    # A path that lexically starts under an allowed root but escapes via ..
    # must be denied (resolve-then-validate).
    result = tool_registry.execute(
        ToolCall(
            name="list_directory",
            arguments={"path": str(Path.home() / "Desktop" / ".." / ".." / ".." / "etc")},
        )
    )
    assert not result.success
    assert result.output == "Access denied."
