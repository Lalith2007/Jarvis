from app.security.permissions import permissions
from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult


class ListDirectoryTool(BaseTool):
    """
    Lists files inside a directory.
    """

    name = "list_directory"

    description = "Lists files in a directory."

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

        # Permission check — resolve-then-validate (previously ungated).
        directory = permissions.resolve_if_allowed(path)
        if directory is None:
            return ToolResult(
                success=False,
                output="Access denied.",
            )

        if not directory.exists():
            return ToolResult(
                success=False,
                output="Directory does not exist.",
            )

        if not directory.is_dir():
            return ToolResult(
                success=False,
                output="Path is not a directory.",
            )

        files = sorted(
            file.name
            for file in directory.iterdir()
        )

        return ToolResult(
            success=True,
            output="\n".join(files),
        )


list_directory_tool = ListDirectoryTool()
