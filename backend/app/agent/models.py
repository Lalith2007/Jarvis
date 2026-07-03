from pydantic import BaseModel

from app.tools.models import ToolResult


class AgentResult(BaseModel):
    tool_used: bool

    tool_result: ToolResult | None = None
