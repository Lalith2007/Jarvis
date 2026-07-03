from enum import Enum

from pydantic import BaseModel, Field, model_validator


class StepType(str, Enum):
    """
    Type of execution step.
    """

    MEMORY = "memory"
    TOOL = "tool"
    LLM = "llm"
    VALIDATION = "validation"
    STORAGE = "storage"


class PlanStep(BaseModel):
    """
    A single executable step.
    """

    id: int

    type: StepType

    description: str

    tool_name: str | None = None

    arguments: dict = Field(default_factory=dict)

    optional: bool = False


class Plan(BaseModel):
    """
    Planner v2 execution graph.

    Legacy constructor fields are retained so the
    existing executor and tests continue to work.
    """

    # -----------------------------
    # Legacy API
    # -----------------------------

    use_tool: bool = False

    tool_name: str | None = None

    arguments: dict = Field(default_factory=dict)

    # -----------------------------
    # Planner v2
    # -----------------------------

    steps: list[PlanStep] = Field(default_factory=list)

    reasoning: str = ""

    estimated_steps: int = 0

    requires_llm: bool = True

    requires_tools: bool = False

    requires_memory: bool = False

    @model_validator(mode="after")
    def build_legacy_step(self):
        """
        Automatically convert legacy plans into
        Planner v2 execution steps.
        """

        if self.steps:
            return self

        if self.use_tool and self.tool_name:

            self.steps.append(
                PlanStep(
                    id=1,
                    type=StepType.TOOL,
                    description=f"Execute {self.tool_name}.",
                    tool_name=self.tool_name,
                    arguments=self.arguments,
                )
            )

            self.requires_tools = True
            self.estimated_steps = 1

        return self
