from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult
from app.tools.registry import ToolRegistry


class DummyTool(BaseTool):
    name = "dummy"
    description = "Dummy tool"

    def execute(self, call: ToolCall) -> ToolResult:
        return ToolResult(
            success=True,
            output="Hello from Dummy Tool",
        )


def test_tool_registry():
    registry = ToolRegistry()

    registry.register(DummyTool())

    result = registry.execute(
        ToolCall(name="dummy")
    )

    assert result.success
    assert result.output == "Hello from Dummy Tool"
