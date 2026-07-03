from abc import ABC, abstractmethod

from app.tools.models import ToolCall, ToolResult


class BaseTool(ABC):
    """
    Base interface for every JARVIS tool.

    Every tool receives a ToolCall object.

    This keeps all tools consistent and makes the
    tool system compatible with planner/executor
    agents, MCP, and future distributed execution.
    """

    name: str

    description: str

    @abstractmethod
    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:
        """
        Execute the tool using a ToolCall.

        Parameters
        ----------
        call:
            Structured tool invocation.

        Returns
        -------
        ToolResult
        """
        raise NotImplementedError
