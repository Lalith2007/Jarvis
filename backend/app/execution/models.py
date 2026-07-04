from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """
    Current state of an execution.
    """

    PENDING = "pending"

    RUNNING = "running"

    WAITING = "waiting"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class Artifact(BaseModel):
    """
    Any artifact produced during execution.

    Examples:
        • Generated image
        • Video
        • Markdown
        • PDF
        • Python file
        • Audio
    """

    name: str

    type: str

    value: Any

    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionStepState(BaseModel):
    """
    Runtime state of a single execution step.
    """

    id: int

    name: str

    status: ExecutionStatus = ExecutionStatus.PENDING

    started_at: datetime | None = None

    finished_at: datetime | None = None

    output: Any = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserState(BaseModel):
    """
    Browser runtime information.
    """

    active: bool = False

    session_id: str | None = None

    current_url: str | None = None

    current_title: str | None = None

    tabs: list[str] = Field(default_factory=list)


class MemoryState(BaseModel):
    """
    Runtime memory available during execution.
    """

    retrieved_notes: list[str] = Field(default_factory=list)

    conversation_context: list[dict] = Field(default_factory=list)


class ModelState(BaseModel):
    """
    Tracks which models participated in execution.
    """

    primary: str | None = None

    secondary: list[str] = Field(default_factory=list)

    reasoning_trace: list[str] = Field(default_factory=list)


class ExecutionContext(BaseModel):
    """
    Shared runtime state for the entire mission.

    Every subsystem reads from and writes to this object.
    """

    mission_id: str

    goal: str

    status: ExecutionStatus = ExecutionStatus.PENDING

    created_at: datetime = Field(default_factory=datetime.now)

    updated_at: datetime = Field(default_factory=datetime.now)

    steps: list[ExecutionStepState] = Field(default_factory=list)

    browser: BrowserState = Field(default_factory=BrowserState)

    memory: MemoryState = Field(default_factory=MemoryState)

    models: ModelState = Field(default_factory=ModelState)

    artifacts: dict[str, Artifact] = Field(default_factory=dict)

    variables: dict[str, Any] = Field(default_factory=dict)

    metadata: dict[str, Any] = Field(default_factory=dict)
