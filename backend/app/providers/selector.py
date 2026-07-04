from app.providers.models import (
    ProviderCapability,
    ProviderModel,
)
from app.providers.registry import provider_registry


class ProviderSelector:
    """
    Selects the best models for a requested set
    of capabilities.

    This class is intentionally independent from
    Athena. It only understands provider metadata.
    """

    def select(
        self,
        *,
        capabilities: list[ProviderCapability],
        limit: int = 3,
    ) -> list[ProviderModel]:

        candidates: list[tuple[int, ProviderModel]] = []

        for model in provider_registry.healthy():

            score = 0

            for capability in capabilities:

                if capability in model.capabilities:
                    score += 1

            if score:
                candidates.append(
                    (
                        score,
                        model,
                    )
                )

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1].context_window,
            ),
            reverse=True,
        )

        return [
            model
            for _, model in candidates[:limit]
        ]


provider_selector = ProviderSelector()
