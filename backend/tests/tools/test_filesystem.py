from pathlib import Path

from app.config.settings import BASE_DIR
from app.tools import tool_registry
from app.tools.models import ToolCall

REPO_ROOT = BASE_DIR.parent  # computed allowed root (no hardcoded path)


def test_list_directory_allowed():
    result = tool_registry.execute(ToolCall(name="list_directory", arguments={"path": str(BASE_DIR)}))
    assert result.success
    assert len(result.output) >= 0


def test_list_directory_denied_home():
    # $HOME itself is not an allowed root -> denied.
    result = tool_registry.execute(ToolCall(name="list_directory", arguments={"path": str(Path.home())}))
    assert not result.success
    assert result.output == "Access denied."


def test_list_directory_denied_traversal():
    escape = str(REPO_ROOT / ".." / ".." / ".." / "etc")
    result = tool_registry.execute(ToolCall(name="list_directory", arguments={"path": escape}))
    assert not result.success
    assert result.output == "Access denied."
