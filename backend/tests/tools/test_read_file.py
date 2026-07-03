from pathlib import Path

from app.tools import tool_registry
from app.tools.models import ToolCall


def test_read_file():
    result = tool_registry.execute(
        ToolCall(
            name="read_file",
            arguments={
                "path": str(Path("README.md")),
            },
        )
    )

    assert result.success
    assert isinstance(result.output, str)
