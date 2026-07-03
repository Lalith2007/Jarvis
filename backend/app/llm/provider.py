from openai import OpenAI

from app.config.settings import settings


class LLMProvider:
    """
    Executes requests against a single LLM provider.

    This class knows nothing about:
        - Athena
        - Routing
        - Retries
        - Multi-model execution

    It only executes one model request.
    """

    def __init__(self):
        self.client = OpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
        )

    def chat(
        self,
        *,
        model: str,
        messages: list[dict],
    ) -> str:

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )

        content = response.choices[0].message.content

        return content or ""


llm_provider = LLMProvider()
