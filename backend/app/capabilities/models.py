from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CapabilityType(str, Enum):
    REASONING = "reasoning"
    CODING = "coding"
    PLANNING = "planning"
    MEMORY = "memory"
    LONG_CONTEXT = "long_context"
    TOOL_USAGE = "tool_usage"
    BROWSER = "browser"
    FILESYSTEM = "filesystem"
    TERMINAL = "terminal"
    PYTHON_RUNTIME = "python_runtime"
    VISION = "vision"
    VOICE = "voice"
    STREAMING = "streaming"
    MCP = "mcp"
    MULTI_MODEL = "multi_model"
    REFLECTION = "reflection"
    BACKGROUND_EXECUTION = "background_execution"
    SCHEDULING = "scheduling"


class CapabilitySource(str, Enum):
    SYSTEM = "system"
    TOOL = "tool"
    MODEL = "model"


class CapabilityPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CapabilityMetadata(BaseModel):
    description: str | None = None
    version: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class CapabilityRequirement(BaseModel):
    capability: CapabilityType
    priority: CapabilityPriority = CapabilityPriority.MEDIUM
    reason: str
    metadata: CapabilityMetadata = Field(default_factory=CapabilityMetadata)


class CapabilityDecision(BaseModel):
    mission_id: str
    required: list[CapabilityRequirement] = Field(default_factory=list)
    approved: bool = False
    reasoning: str = ""


class MissionCapabilities(BaseModel):
    decision: CapabilityDecision
    active: list[CapabilityType] = Field(default_factory=list)


class CapabilityAnalysis(BaseModel):
    detected: list[CapabilityRequirement] = Field(default_factory=list)
    missing: list[CapabilityType] = Field(default_factory=list)
    score: float = 0.0


class ExecutionRequirement(BaseModel):
    capabilities: list[CapabilityType] = Field(default_factory=list)
    strict: bool = True
