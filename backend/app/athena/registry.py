from app.athena.models import ModelInfo, ModelType
from app.athena.profiles import MODEL_PROFILES


class ModelRegistry:
    """
    Stores runtime information about every model.
    """

    def __init__(self):
        self._models = {
            model: ModelInfo(
                model=model,
                profile=profile,
            )
            for model, profile in MODEL_PROFILES.items()
        }

    def get(
        self,
        model: ModelType,
    ) -> ModelInfo:
        return self._models[model]

    def all(self):
        return self._models

    def enabled(self):
        return {
            model: info
            for model, info in self._models.items()
            if info.enabled
        }

    def verified(self):
        """
        Models that are both enabled and healthy.
        """
        return {
            model: info
            for model, info in self._models.items()
            if (
                info.enabled
                and info.healthy
            )
        }

    def healthy(self):
        return {
            model: info
            for model, info in self._models.items()
            if (
                info.enabled
                and info.healthy
            )
        }


model_registry = ModelRegistry()
