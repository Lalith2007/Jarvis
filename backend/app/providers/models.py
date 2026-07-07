from enum import Enum

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    """
    Supported LLM providers.
    """

    NVIDIA = "nvidia"

    OPENAI = "openai"

    OPENROUTER = "openrouter"

    ANTHROPIC = "anthropic"

    OLLAMA = "ollama"

    GOOGLE = "google"


class ProviderCapability(str, Enum):
    """
    Capabilities exposed by a provider/model.
    """

    CHAT = "chat"

    REASONING = "reasoning"

    CODING = "coding"

    VISION = "vision"

    TOOLS = "tools"

    LONG_CONTEXT = "long_context"

    STREAMING = "streaming"


class ProviderModel(BaseModel):
    """
    Metadata describing a single model.
    """

    id: str

    provider: ProviderType

    display_name: str

    context_window: int

    enabled: bool = True

    healthy: bool = True

    # Measured mean response latency (ms) from the last health probe; None until
    # probed. Used by ModelRankingEngine to prefer responsive models.
    avg_latency_ms: float | None = None

    capabilities: list[ProviderCapability] = Field(
        default_factory=list
    )
