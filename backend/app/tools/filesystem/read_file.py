from app.security.permissions import permissions
from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult


class ReadFileTool(BaseTool):
    name = "read_file"

    description = "Reads a text file."

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        path = call.arguments.get("path")

        if path is None:
            return ToolResult(
                success=False,
                output="Missing required argument: path",
            )

        # Permission check — resolve-then-validate, operate on resolved path.
        file = permissions.resolve_if_allowed(path)
        if file is None:
            return ToolResult(
                success=False,
                output="Access denied.",
            )

        if not file.exists():
            return ToolResult(
                success=False,
                output="File not found.",
            )

        if not file.is_file():
            return ToolResult(
                success=False,
                output="Path is not a file.",
            )

        return ToolResult(
            success=True,
            output=file.read_text(
                encoding="utf-8",
            ),
        )


read_file_tool = ReadFileTool()
