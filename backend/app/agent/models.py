from pydantic import BaseModel, Field

from app.tools.models import ToolResult


class AgentResult(BaseModel):
    tool_used: bool

    tool_result: ToolResult | None = None

    metadata: dict = Field(default_factory=dict)
    
    mission_id: str | None = None

