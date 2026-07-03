from enum import IntEnum

from pydantic import BaseModel


class TaskComplexity(IntEnum):
    """
    Overall difficulty of the user's request.
    """

    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    EXPERT = 5


class ContextRequirement(IntEnum):
    """
    Approximate context window required to solve the task.
    """

    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    VERY_LARGE = 4


class TaskAnalysis(BaseModel):
    """
    High-level description of a task.

    This is independent of any particular model.
    Athena uses this information when selecting
    one or more models.
    """

    complexity: TaskComplexity

    context_requirement: ContextRequirement

    requires_tools: bool

    requires_memory: bool

    requires_reasoning: bool

    requires_multimodel: bool

    latency_priority: int

    cost_priority: int
