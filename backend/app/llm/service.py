from openai import OpenAI

from app.config.settings import settings
from app.llm.prompts.loader import prompt_loader


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
        )

        self.system_prompt = prompt_loader.load("system.md")

    def chat(self, messages: list[dict]) -> str:
        conversation = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        conversation.extend(messages)

        response = self.client.chat.completions.create(
            model=settings.MODEL,
            messages=conversation,
        )

        return response.choices[0].message.content


llm = LLMService()
