from app.agents.hermes.models import PromptContext
from app.athena.router import athena
from app.llm.builder import message_builder
from app.llm.orchestrator import llm_orchestrator
from app.platform.publisher import EventPublisher


class LLMService:
    """
    Public interface for all LLM interactions.

    Responsibilities:
        • Build prompt messages
        • Request routing decisions from Athena (with events)
        • Delegate execution to the orchestrator
    """

    def _build_messages(
        self,
        context: PromptContext,
    ) -> list[dict]:
        """Backwards-compatible wrapper."""
        return message_builder.build(context)

    def _route(self, context: PromptContext):
        """
        Invoke Athena and emit AthenaStarted / AthenaCompleted events.
        Returns a RouteDecision.
        """
        session_id = context.metadata.get("session_id") if context.metadata else None

        EventPublisher.publish(
            subsystem="athena",
            event_type="AthenaStarted",
            payload={"session_id": session_id, "query": context.user_query},
        )

        decision = athena.route(context)

        EventPublisher.publish(
            subsystem="athena",
            event_type="AthenaCompleted",
            payload={
                "session_id": session_id,
                "primary_model": decision.primary.value,
                "reason": decision.reason,
            },
        )

        return decision



    def chat(
        self,
        context: PromptContext,
    ) -> str:

        decision = self._route(context)
        messages = self._build_messages(context)
        
        return llm_orchestrator.execute(
            decision=decision,
            messages=messages,
            context=context,
        )

    def stream(
        self,
        context: PromptContext,
    ):
        """
        Stream LLM tokens as a synchronous generator.
        Yields str chunks.
        """
        decision = self._route(context)
        messages = self._build_messages(context)
        
        yield from llm_orchestrator.execute_stream(
            decision=decision,
            messages=messages,
            context=context,
        )


llm = LLMService()
