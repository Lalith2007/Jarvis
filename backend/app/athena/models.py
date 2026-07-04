from enum import Enum

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


class ModelRecommendation(BaseModel):
    """
    Athena's recommendation for a model.

    Future versions may include:
        • Historical success rate
        • Runtime latency
        • Cost estimation
        • Confidence
        • Health
    """

    model: ModelType

    score: float

    confidence: float | None = None

    estimated_cost: float | None = None

    estimated_latency: float | None = None

    healthy: bool = True

    reasons: list[str] = Field(default_factory=list)


class RouteDecision(BaseModel):
    """
    Final routing decision returned by Athena.
    """

    primary: ModelType

    recommendations: list[ModelRecommendation]

    reason: str


class ModelInfo(BaseModel):
    """
    Static metadata stored in Athena's model registry.
    """

    profile: object

    enabled: bool = True

    healthy: bool = True
