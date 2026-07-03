from app.agents.hermes.models import PromptContext
from app.athena.router import athena
from app.llm.builder import message_builder
from app.llm.orchestrator import llm_orchestrator


class LLMService:
    """
    Public interface for all LLM interactions.

    Responsibilities:
        • Build prompt messages
        • Request routing decisions from Athena
        • Delegate execution to the orchestrator

    The _build_messages() method is retained as a
    backwards-compatible wrapper for existing tests
    and legacy callers.
    """

    def _build_messages(
        self,
        context: PromptContext,
    ) -> list[dict]:
        """
        Backwards-compatible wrapper.

        Delegates message construction to the
        MessageBuilder component.
        """
        return message_builder.build(context)

    def chat(
        self,
        context: PromptContext,
    ) -> str:

        print("[LLM] Routing request...")

        decision = athena.route(context)

        messages = self._build_messages(context)

        return llm_orchestrator.execute(
            decision=decision,
            messages=messages,
        )


llm = LLMService()
