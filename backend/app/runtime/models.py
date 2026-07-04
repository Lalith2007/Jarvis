from enum import Enum
from typing import Any
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from app.capabilities.models import CapabilityType

class RuntimeStatus(str, Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANED_UP = "cleaned_up"

class RuntimeResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)
    execution_time_ms: float = 0.0

class SecurityAction(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    CONNECT = "connect"

class RuntimePermission(BaseModel):
    capability: CapabilityType
    action: SecurityAction
    resource: str | None = None
