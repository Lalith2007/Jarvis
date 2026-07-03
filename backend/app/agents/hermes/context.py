from app.agents.hermes.models import PromptContext


def validate_context(context: PromptContext) -> None:
    if not context.system_prompt:
        raise ValueError("Missing system prompt")

    if not context.user_query.strip():
        raise ValueError("Empty user query")
