from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CapabilityCategory(str, Enum):
    LLM = "LLM"
    MEMORY = "Memory"
    PLANNER = "Planner"
    TOOL = "Tool"
    BROWSER = "Browser"
    FILESYSTEM = "Filesystem"
    PYTHON = "Python"
    VISION = "Vision"
    VOICE = "Voice"
    NETWORK = "Network"
    SYSTEM = "System"
    REFLECTION = "Reflection"
    CUSTOM = "Custom"


class CapabilityManifest(BaseModel):
    id: str
    name: str
    version: str
    author: str
    description: str
    category: CapabilityCategory
    permissions: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    supported_inputs: List[str] = Field(default_factory=list)
    supported_outputs: List[str] = Field(default_factory=list)
    configuration_schema: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    enabled_by_default: bool = True
    
    # Scheduling Hints
    preferred_parallelism: int = 1
    exclusive_execution: bool = False
    estimated_memory: int = 128  # MB
    estimated_cpu: float = 0.1  # cores


class CapabilityConfig(BaseModel):
    static_config: Dict[str, Any] = Field(default_factory=dict)
    runtime_config: Dict[str, Any] = Field(default_factory=dict)
    environment_config: Dict[str, Any] = Field(default_factory=dict)


class CapabilityContext(BaseModel):
    mission_id: str
    graph_id: str
    execution_id: str
    node_id: str
    athena_decision: Optional[Any] = None  # To avoid circular import, we can leave as Any or dict
    memory_plan: Optional[Any] = None
    resource_budget: Dict[str, Any] = Field(default_factory=dict)
    runtime_state: Dict[str, Any] = Field(default_factory=dict)
    
    # Sandbox isolation
    approved_resources: List[str] = Field(default_factory=list)


class CapabilityDiagnostics(BaseModel):
    initialized_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0
    exceptions: List[str] = Field(default_factory=list)
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    dependency_chain: List[str] = Field(default_factory=list)
    execution_trace: List[str] = Field(default_factory=list)


class CapabilityResult(BaseModel):
    success: bool
    status: str
    result: Any = None
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: CapabilityDiagnostics = Field(default_factory=CapabilityDiagnostics)


class CapabilityMetrics(BaseModel):
    execution_count: int = 0
    failure_count: int = 0
    average_latency: float = 0.0
    average_cost: float = 0.0
    last_execution: Optional[datetime] = None
    health_score: float = 100.0
