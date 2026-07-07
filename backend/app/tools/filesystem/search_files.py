from app.security.permissions import permissions
from app.tools.base import BaseTool
from app.tools.models import ToolCall, ToolResult


class SearchFilesTool(BaseTool):
    """
    Searches files recursively.
    """

    name = "search_files"

    description = "Search files by name."

    def execute(
        self,
        call: ToolCall,
    ) -> ToolResult:

        path = call.arguments.get("path")
        pattern = call.arguments.get("pattern")

        if path is None:
            return ToolResult(
                success=False,
                output="Missing required argument: path",
            )

        if pattern is None:
            return ToolResult(
                success=False,
                output="Missing required argument: pattern",
            )

        root = permissions.resolve_if_allowed(path)
        if root is None:
            return ToolResult(
                success=False,
                output="Access denied.",
            )

        if not root.exists():
            return ToolResult(
                success=False,
                output="Directory not found.",
            )

        matches = [
            str(file)
            for file in root.rglob("*")
            if pattern.lower() in file.name.lower()
        ]

        return ToolResult(
            success=True,
            output="\n".join(matches),
            metadata={
                "count": len(matches),
            },
        )


search_files_tool = SearchFilesTool()
