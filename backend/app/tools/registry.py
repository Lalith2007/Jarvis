from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult


class ToolRegistry:
    """
    Registry for all available tools.
    """

    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:

        self.tools[tool.name] = tool

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        tool = self.tools.get(call.name)

        if tool is None:
            return ToolResult(
                success=False,
                output=f"Unknown tool: {call.name}",
            )

        return tool.execute(call)


tool_registry = ToolRegistry()
