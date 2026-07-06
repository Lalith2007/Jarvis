from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    LLM = "llm"
    MEMORY = "memory"
    TOOL = "tool"
    PLANNER = "planner"
    RUNTIME = "runtime"
    AGGREGATOR = "aggregator"


class NodeStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionNode(BaseModel):
    id: str
    type: NodeType
    status: NodeStatus = NodeStatus.PENDING
    dependencies: list[str] = Field(default_factory=list)
    
    # Capability-driven execution
    capability: str
    payload: dict[str, Any] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    # Metrics
    queue_time_ms: float = 0.0
    execution_time_ms: float = 0.0
    capability_latency: float = 0.0
    
    # Control
    retry_count: int = 0
    timeout: float = 60.0  # seconds
    
    # Output
    result: Any | None = None


class MissionGraph(BaseModel):
    graph_id: str
    schema_version: str = "1.0"
    graph_version: str = "1.0"

    nodes: dict[str, MissionNode] = Field(default_factory=dict)

    # The AthenaDecision that produced this graph — serialised as dict to avoid
    # circular imports.  runtime.generate consumes this to skip the second
    # Athena routing pass (unified Athena authority).
    athena_decision: dict[str, Any] | None = None

    # Metrics
    graph_duration_ms: float = 0.0
    successful_nodes: int = 0
    failed_nodes: int = 0
    
    # Persistence
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
        
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MissionGraph":
        return cls.model_validate(data)
        
    def to_json(self) -> str:
        return self.model_dump_json()
        
    @classmethod
    def from_json(cls, json_str: str) -> "MissionGraph":
        return cls.model_validate_json(json_str)

