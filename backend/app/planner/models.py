from pydantic import BaseModel, Field


class Plan(BaseModel):
    use_tool: bool

    tool_name: str | None = None

    arguments: dict = Field(default_factory=dict)

    reasoning: str = ""
