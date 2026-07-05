import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class PlatformEvent(BaseModel):
    schema_version: str = "1.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: Optional[str] = None
    session_id: Optional[str] = None
    execution_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    subsystem: str
    event_type: str
    status: str = "success"
    severity: str = "info"
    duration_ms: int = 0
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

