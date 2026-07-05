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

    def stream(
        self,
        *,
        model: str,
        messages: list[dict],
    ):
        """
        Stream tokens from the LLM provider.

        Yields str chunks as they arrive.
        """
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta


llm_provider = LLMProvider()
