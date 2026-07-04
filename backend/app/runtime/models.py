from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class RuntimeStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class RuntimeResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)
