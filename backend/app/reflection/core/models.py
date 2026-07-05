import json
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class ReflectionCategory(str, Enum):
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    CAPABILITY_USAGE = "capability_usage"
    MEMORY_USAGE = "memory_usage"
    PLANNING = "planning"
    ROUTING = "routing"
    EXECUTION = "execution"
    RESOURCE_CONSUMPTION = "resource_consumption"

class LessonSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Lesson(BaseModel):
    category: ReflectionCategory
    confidence: float
    severity: LessonSeverity
    impact: str
    recommendation: str
    supporting_evidence: Dict[str, Any] = Field(default_factory=dict)

class ImprovementPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ImprovementSuggestion(BaseModel):
    category: ReflectionCategory
    description: str
    expected_benefit: str
    implementation_priority: ImprovementPriority
    confidence: float

class ReflectionMetrics(BaseModel):
    mission_duration_ms: float = 0.0
    graph_duration_ms: float = 0.0
    capability_breakdown: Dict[str, int] = Field(default_factory=dict)
    parallelism_score: float = 1.0
    retry_statistics: Dict[str, int] = Field(default_factory=dict)
    failure_statistics: Dict[str, int] = Field(default_factory=dict)
    resource_usage: Dict[str, float] = Field(default_factory=dict)
    budget_usage_percentage: float = 0.0
    success_rate: float = 0.0

class MissionSummary(BaseModel):
    mission_id: str
    session_id: Optional[str] = None
    success: bool
    total_nodes: int
    successful_nodes: int
    failed_nodes: int
    goal: Optional[str] = None
    result: Optional[Any] = None

class ReflectionStep(BaseModel):
    analyzer_name: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    lessons: List[Lesson] = Field(default_factory=list)
    suggestions: List[ImprovementSuggestion] = Field(default_factory=list)

class ReflectionResult(BaseModel):
    mission_id: str
    summary: MissionSummary
    metrics: ReflectionMetrics
    steps: List[ReflectionStep] = Field(default_factory=list)
    lessons: List[Lesson] = Field(default_factory=list)
    suggestions: List[ImprovementSuggestion] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReflectionResult":
        return cls(**data)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, data: str) -> "ReflectionResult":
        return cls.model_validate_json(data)
