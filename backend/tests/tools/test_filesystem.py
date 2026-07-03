from pathlib import Path

from app.tools import tool_registry
from app.tools.models import ToolCall


def test_list_directory():
    result = tool_registry.execute(
        ToolCall(
            name="list_directory",
            arguments={
                "path": str(Path.home()),
            },
        )
    )

    assert result.success
    assert len(result.output) > 0
