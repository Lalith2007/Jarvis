from openai import OpenAI

from app.athena.models import ModelType
from app.athena.registry import model_registry
from app.config.settings import settings


class ModelVerifier:
    """
    Verifies whether registered models
    are callable.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
        )

    def verify(
        self,
        model: ModelType,
    ) -> bool:

        try:

            self.client.chat.completions.create(
                model=model.value,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply only with OK."
                    }
                ],
                max_tokens=16,
                timeout=20,
            )

            info = model_registry.get(model)
            info.healthy = True

            return True

        except Exception:

            info = model_registry.get(model)
            info.healthy = False

            return False


verifier = ModelVerifier()
