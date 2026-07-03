from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


class ToolResult(BaseModel):
    success: bool

    output: str

    metadata: dict = Field(default_factory=dict)
