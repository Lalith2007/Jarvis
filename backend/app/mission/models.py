from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MissionStatus(str, Enum):
    """
    Current lifecycle state of a mission.
    """

    CREATED = "created"

    ANALYZING = "analyzing"

    PLANNING = "planning"

    EXECUTING = "executing"

    WAITING = "waiting"

    REFLECTING = "reflecting"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class MissionPriority(str, Enum):
    """
    Scheduling priority.
    """

    LOW = "low"

    NORMAL = "normal"

    HIGH = "high"

    CRITICAL = "critical"


class MissionResult(BaseModel):
    """
    Final output returned by a completed mission.
    """

    success: bool = False

    response: str = ""

    artifacts: list[str] = Field(default_factory=list)

    models_used: list[str] = Field(default_factory=list)

    tools_used: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class Mission(BaseModel):
    """
    Represents a user goal.

    A Mission owns the lifecycle of a goal.
    Execution contexts, retries, browser sessions,
    MCP calls, etc. belong to the mission.
    """

    id: str

    @property
    def mission_id(self) -> str:
        return self.id

    graph_id: str | None = None
    
    execution_id: str | None = None

    goal: str

    status: MissionStatus = MissionStatus.CREATED

    priority: MissionPriority = MissionPriority.NORMAL

    execution_ids: list[str] = Field(default_factory=list)

    result: MissionResult = Field(default_factory=MissionResult)

    created_at: datetime = Field(default_factory=datetime.now)

    updated_at: datetime = Field(default_factory=datetime.now)

    metadata: dict[str, Any] = Field(default_factory=dict)
