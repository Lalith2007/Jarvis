from pathlib import Path

from app.tools import tool_registry
from app.tools.models import ToolCall


def test_search_files():
    result = tool_registry.execute(
        ToolCall(
            name="search_files",
            arguments={
                "path": str(Path.cwd()),
                "pattern": "README",
            },
        )
    )

    assert result.success
