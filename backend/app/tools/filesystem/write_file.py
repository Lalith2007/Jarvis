from pathlib import Path

from app.security.permissions import permissions
from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult


class WriteFileTool(BaseTool):
    name = "write_file"

    description = "Writes text to a file."

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        path = call.arguments.get("path")
        content = call.arguments.get("content")

        if path is None:
            return ToolResult(
                success=False,
                output="Missing required argument: path",
            )

        if content is None:
            return ToolResult(
                success=False,
                output="Missing required argument: content",
            )

        # Permission check
        if not permissions.allowed(path):
            return ToolResult(
                success=False,
                output="Access denied.",
            )

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.write_text(
            content,
            encoding="utf-8",
        )

        return ToolResult(
            success=True,
            output=f"Successfully wrote to {file}",
        )


write_file_tool = WriteFileTool()
