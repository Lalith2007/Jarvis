from app.providers.models import (
    ProviderCapability,
    ProviderModel,
    ProviderType,
)


class ProviderRegistry:
    """
    Central registry of all models available to JARVIS.

    This registry is the single source of truth for
    provider/model metadata.

    Athena, the LLM orchestrator, and future routing
    policies will consume this registry instead of
    hardcoding model information.
    """

    def __init__(self):
        self._models: dict[str, ProviderModel] = {}

        self._register_defaults()

    def _register_defaults(self) -> None:

        self.register(
            ProviderModel(
                id="z-ai/glm-5.2",
                provider=ProviderType.NVIDIA,
                display_name="GLM-5.2",
                context_window=1_000_000,
                capabilities=[
                    ProviderCapability.CHAT,
                    ProviderCapability.REASONING,
                    ProviderCapability.CODING,
                    ProviderCapability.TOOLS,
                    ProviderCapability.LONG_CONTEXT,
                    ProviderCapability.STREAMING,
                ],
            )
        )

        self.register(
            ProviderModel(
                id="deepseek-ai/deepseek-v4-pro",
                provider=ProviderType.NVIDIA,
                display_name="DeepSeek V4 Pro",
                context_window=128_000,
                capabilities=[
                    ProviderCapability.CHAT,
                    ProviderCapability.CODING,
                    ProviderCapability.TOOLS,
                    ProviderCapability.STREAMING,
                ],
            )
        )

        self.register(
            ProviderModel(
                id="openai/gpt-oss-120b",
                provider=ProviderType.NVIDIA,
                display_name="GPT-OSS 120B",
                context_window=128_000,
                capabilities=[
                    ProviderCapability.CHAT,
                    ProviderCapability.REASONING,
                    ProviderCapability.STREAMING,
                ],
            )
        )

        self.register(
            ProviderModel(
                id="nvidia/nemotron-3-ultra-550b-a55b",
                provider=ProviderType.NVIDIA,
                display_name="Nemotron Ultra",
                context_window=128_000,
                capabilities=[
                    ProviderCapability.CHAT,
                    ProviderCapability.REASONING,
                    ProviderCapability.STREAMING,
                ],
            )
        )

        self.register(
            ProviderModel(
                id="minimaxai/minimax-m3",
                provider=ProviderType.NVIDIA,
                display_name="MiniMax M3",
                context_window=1_000_000,
                capabilities=[
                    ProviderCapability.CHAT,
                    ProviderCapability.LONG_CONTEXT,
                    ProviderCapability.REASONING,
                ],
            )
        )

        self.register(
            ProviderModel(
                id="meta/llama-3.1-70b-instruct",
                provider=ProviderType.NVIDIA,
                display_name="Llama 3.1 70B",
                context_window=128_000,
                capabilities=[
                    ProviderCapability.CHAT,
                ],
            )
        )

    def register(
        self,
        model: ProviderModel,
    ) -> None:

        self._models[model.id] = model

    def get(
        self,
        model_id: str,
    ) -> ProviderModel | None:

        return self._models.get(model_id)

    def all(
        self,
    ) -> list[ProviderModel]:

        return list(self._models.values())

    def enabled(
        self,
    ) -> list[ProviderModel]:

        return [
            model
            for model in self._models.values()
            if model.enabled
        ]

    def healthy(
        self,
    ) -> list[ProviderModel]:

        return [
            model
            for model in self._models.values()
            if model.enabled
            and model.healthy
        ]

    def probe_health(self, timeout: float = 8.0) -> dict[str, bool]:
        """
        Live health check: ping each enabled model with a 1-token chat and set
        `healthy` from the real result. This replaces the previously-hardcoded
        `healthy=True` so routing never selects a model that does not respond.

        Makes network calls — call at startup (env-gated) or on demand, not in
        the hot path. Returns {model_id: healthy}.
        """
        import logging

        from openai import OpenAI

        from app.config.settings import settings

        logger = logging.getLogger(__name__)
        client = OpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
            timeout=timeout,
            max_retries=0,
        )
        results: dict[str, bool] = {}
        for model in self._models.values():
            if not model.enabled:
                results[model.id] = False
                continue
            try:
                client.chat.completions.create(
                    model=model.id,
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=1,
                )
                model.healthy = True
            except Exception as exc:  # noqa: BLE001 — any failure => unhealthy
                model.healthy = False
                logger.warning("Model %s failed health probe: %s", model.id, exc)
            results[model.id] = model.healthy
        return results


provider_registry = ProviderRegistry()
