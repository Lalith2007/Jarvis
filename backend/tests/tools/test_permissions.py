from app.tools import tool_registry
from app.tools.models import ToolCall


def test_read_denied():
    result = tool_registry.execute(
        ToolCall(
            name="read_file",
            arguments={
                "path": "/etc/passwd",
            },
        )
    )

    assert not result.success
    assert result.output == "Access denied."


def test_write_denied():
    result = tool_registry.execute(
        ToolCall(
            name="write_file",
            arguments={
                "path": "/etc/test.txt",
                "content": "Hello",
            },
        )
    )

    assert not result.success
    assert result.output == "Access denied."
