from openai import OpenAI

from app.agents.hermes.models import PromptContext
from app.athena.router import athena
from app.config.settings import settings


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
        )

    def _build_messages(
        self,
        context: PromptContext,
    ) -> list[dict]:

        messages = [
            {
                "role": "system",
                "content": context.system_prompt,
            }
        ]

        if context.knowledge:

            knowledge = "\n\n".join(
                [
                    f"# {result.note.title}\n{result.note.content}"
                    for result in context.knowledge
                ]
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant knowledge from the user's vault:\n\n"
                        + knowledge
                    ),
                }
            )

        if context.tool_results:

            tool_output = "\n\n".join(
                [
                    f"Tool: {tool.get('tool_name', 'Unknown')}\n"
                    f"Success: {tool.get('success', False)}\n"
                    f"Output:\n{tool.get('output', '')}"
                    for tool in context.tool_results
                ]
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Recent tool execution results:\n\n"
                        + tool_output
                    ),
                }
            )

        messages.extend(context.conversation)

        messages.append(
            {
                "role": "user",
                "content": context.user_query,
            }
        )

        return messages

    def chat(
        self,
        context: PromptContext,
    ) -> str:

        print("[LLM] Routing request...")

        decision = athena.route(context)

        messages = self._build_messages(context)

        print(
            f"[Athena] Primary: {decision.primary.value}"
        )

        for recommendation in decision.recommendations:

            model = recommendation.model.value

            print(f"[LLM] Trying {model}")

            try:

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                )

                print(f"[LLM] Success: {model}")

                return response.choices[0].message.content

            except Exception as exc:

                print(
                    f"[LLM] Failed: {model}"
                )

                print(exc)

        raise RuntimeError(
            "All recommended models failed."
        )


llm = LLMService()
