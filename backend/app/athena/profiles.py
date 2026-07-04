from pydantic import BaseModel

from app.athena.capabilities import Capability
from app.athena.models import ModelType


class ModelProfile(BaseModel):
    """
    Describes the static capabilities of a model.

    Athena uses these values as the foundation for
    scoring and routing decisions.
    """

    model: ModelType

    strengths: list[str]

    routing_keywords: list[str]

    capabilities: dict[Capability, int]

    max_context: int

    description: str


MODEL_PROFILES = {

    ModelType.GLM_52: ModelProfile(
        model=ModelType.GLM_52,

        strengths=[
            "agentic reasoning",
            "software engineering",
            "planning",
            "tool usage",
            "long horizon reasoning",
            "multi-step execution",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 100,
            Capability.EXECUTION: 100,
            Capability.TOOL_USAGE: 100,
            Capability.PLANNING: 100,
            Capability.RESEARCH: 95,
            Capability.DOCUMENTS: 90,
            Capability.KNOWLEDGE: 95,
            Capability.BUSINESS: 90,
            Capability.FINANCE: 90,
            Capability.TRADING: 85,
            Capability.MONEY: 90,
            Capability.WRITING: 90,
            Capability.CONVERSATION: 90,
        },

        max_context=1_000_000,

        description="Flagship reasoning and agentic execution model.",
    ),

    ModelType.DEEPSEEK: ModelProfile(
        model=ModelType.DEEPSEEK,

        strengths=[
            "software engineering",
            "debugging",
            "implementation",
            "technical reasoning",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 100,
            Capability.EXECUTION: 95,
            Capability.TOOL_USAGE: 90,
            Capability.PLANNING: 70,
            Capability.RESEARCH: 60,
            Capability.DOCUMENTS: 40,
            Capability.KNOWLEDGE: 55,
            Capability.BUSINESS: 70,
            Capability.FINANCE: 55,
            Capability.TRADING: 55,
            Capability.MONEY: 65,
            Capability.WRITING: 55,
            Capability.CONVERSATION: 60,
        },

        max_context=128000,

        description="Software engineering specialist.",
    ),

    ModelType.NEMOTRON: ModelProfile(
        model=ModelType.NEMOTRON,

        strengths=[
            "planning",
            "reasoning",
            "decision making",
            "multi-agent orchestration",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 70,
            Capability.EXECUTION: 80,
            Capability.PLANNING: 100,
            Capability.RESEARCH: 90,
            Capability.DOCUMENTS: 70,
            Capability.KNOWLEDGE: 75,
            Capability.BUSINESS: 95,
            Capability.FINANCE: 90,
            Capability.TRADING: 85,
            Capability.MONEY: 95,
            Capability.WRITING: 75,
            Capability.CONVERSATION: 75,
            Capability.TOOL_USAGE: 65,
        },

        max_context=128000,

        description="Planning and reasoning specialist.",
    ),

    ModelType.MINIMAX: ModelProfile(
        model=ModelType.MINIMAX,

        strengths=[
            "long context",
            "research",
            "summarization",
            "knowledge synthesis",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 30,
            Capability.EXECUTION: 40,
            Capability.PLANNING: 80,
            Capability.RESEARCH: 100,
            Capability.DOCUMENTS: 100,
            Capability.KNOWLEDGE: 95,
            Capability.BUSINESS: 70,
            Capability.FINANCE: 65,
            Capability.TRADING: 65,
            Capability.MONEY: 70,
            Capability.WRITING: 65,
            Capability.CONVERSATION: 70,
            Capability.TOOL_USAGE: 40,
        },

        max_context=1_000_000,

        description="Research and long-context specialist.",
    ),

    ModelType.GPT_OSS_120B: ModelProfile(
        model=ModelType.GPT_OSS_120B,

        strengths=[
            "general reasoning",
            "conversation",
            "writing",
            "education",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 80,
            Capability.EXECUTION: 70,
            Capability.PLANNING: 85,
            Capability.RESEARCH: 80,
            Capability.DOCUMENTS: 70,
            Capability.KNOWLEDGE: 75,
            Capability.BUSINESS: 85,
            Capability.FINANCE: 80,
            Capability.TRADING: 75,
            Capability.MONEY: 85,
            Capability.WRITING: 95,
            Capability.CONVERSATION: 100,
            Capability.TOOL_USAGE: 70,
        },

        max_context=128000,

        description="General-purpose reasoning model.",
    ),

    ModelType.LLAMA31: ModelProfile(
        model=ModelType.LLAMA31,

        strengths=[
            "fallback",
            "conversation",
        ],

        routing_keywords=[],

        capabilities={
            Capability.CODING: 65,
            Capability.EXECUTION: 60,
            Capability.PLANNING: 70,
            Capability.RESEARCH: 65,
            Capability.DOCUMENTS: 60,
            Capability.KNOWLEDGE: 65,
            Capability.BUSINESS: 70,
            Capability.FINANCE: 65,
            Capability.TRADING: 60,
            Capability.MONEY: 65,
            Capability.WRITING: 80,
            Capability.CONVERSATION: 85,
            Capability.TOOL_USAGE: 60,
        },

        max_context=128000,

        description="Reliable fallback model.",
    ),
}
