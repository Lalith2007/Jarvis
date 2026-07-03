from pydantic import BaseModel, Field

from app.planner.models import PlanStep
from app.tools.models import ToolResult


class StepResult(BaseModel):
    """
    Result of executing a single plan step.
    """

    step: PlanStep

    success: bool

    output: str = ""

    metadata: dict = Field(default_factory=dict)

    tool_result: ToolResult | None = None
