from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """
    Canonical list of models supported by JARVIS.

    Athena reasons only about ModelType values.
    The LLM layer is responsible for executing them.
    """

    GLM_52 = "z-ai/glm-5.2"
    DEEPSEEK = "deepseek-ai/deepseek-v4-pro"
    NEMOTRON = "nvidia/nemotron-3-ultra-550b-a55b"
    MINIMAX = "minimaxai/minimax-m3"
    GPT_OSS_120B = "openai/gpt-oss-120b"
    LLAMA31 = "meta/llama-3.1-70b-instruct"


class IntentClass(str, Enum):
    conversation = "conversation"
    research = "research"
    coding = "coding"
    planning = "planning"
    automation = "automation"
    retrieval = "retrieval"
    summarization = "summarization"
    analysis = "analysis"
    generation = "generation"
    multimodal = "multimodal"
    unknown = "unknown"


class ComplexityClass(str, Enum):
    trivial = "trivial"
    low = "low"
    medium = "medium"
    high = "high"
    expert = "expert"


class ExecutionStrategy(str, Enum):
    sequential = "sequential"
    parallel = "parallel"
    hybrid = "hybrid"


class MemoryStrategy(str, Enum):
    none = "none"
    working = "working"
    semantic = "semantic"
    episodic = "episodic"
    procedural = "procedural"
    combined = "combined"


class ModelRecommendation(BaseModel):
    """
    Athena's recommendation for a model.
    """
    model: ModelType
    score: float
    confidence: float | None = None
    estimated_cost: float | None = None
    estimated_latency: float | None = None
    healthy: bool = True
    reason: str = ""
    reasons: list[str] = Field(default_factory=list)


class RouteDecision(BaseModel):
    """
    Final routing decision returned by Athena for LLM orchestration.
    """
    primary: ModelType
    recommendations: List[ModelRecommendation]
    reason: str


class CapabilityRecommendation(BaseModel):
    capability: str
    confidence: float
    priority: str
    reason: str
    estimated_latency: float
    estimated_cost: float
    required: bool
    parallelizable: bool


class MemoryPlan(BaseModel):
    strategy: MemoryStrategy
    retrieval_required: bool
    write_required: bool
    reflection_required: bool
    expected_memories: int
    retrieval_budget: float


class AthenaDecision(BaseModel):
    intent: IntentClass
    task_type: str
    complexity: ComplexityClass
    estimated_cost: float
    estimated_latency: float
    confidence: float
    
    memory_plan: MemoryPlan
    execution_strategy: ExecutionStrategy
    recommended_capabilities: List[CapabilityRecommendation]
    recommended_models: List[ModelRecommendation]
    
    requires_parallel_execution: bool
    requires_reflection: bool
    requires_memory: bool
    requires_tools: bool
    
    risk_level: str
    reasoning_summary: str
    
    token_budget: int
    latency_budget_ms: float
    cost_budget: float
    maximum_parallelism: int
    
    decision_trace: List[str] = Field(default_factory=list)


class ModelInfo(BaseModel):
    """
    Static metadata stored in Athena's model registry.
    """
    profile: object
    enabled: bool = True
    healthy: bool = True
