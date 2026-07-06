from app.agents.hermes.models import PromptContext
from app.athena.models import RouteDecision
from app.athena.router import athena
from app.llm.builder import message_builder
from app.llm.orchestrator import llm_orchestrator
from app.platform.publisher import EventPublisher


class LLMService:
    """
    Public interface for all LLM interactions.

    Responsibilities:
        • Build prompt messages
        • Request routing decisions from Athena when no pre-computed
          RouteDecision is supplied (fallback path only)
        • Delegate execution to the orchestrator

    Sprint 12.8 — Unified Athena Authority:
    chat() and stream() now accept an optional pre-computed RouteDecision.
    When one is provided the legacy athena.route() call is skipped entirely,
    eliminating the redundant second Athena routing pass that was identified
    in the Sprint 12.7 forensic review.
    """

    def _build_messages(self, context: PromptContext) -> list[dict]:
        return message_builder.build(context)

    def _route(self, context: PromptContext) -> RouteDecision:
        """
        Fallback routing via the legacy Athena router.
        Called only when runtime.generate does not carry a pre-computed
        AthenaDecision (e.g. legacy test paths or missing metadata).
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
        route_decision: RouteDecision | None = None,
    ) -> str:
        """
        Synchronous LLM call.

        Args:
            context: Full prompt context built by ContextBuilder.
            route_decision: Pre-computed RouteDecision from AthenaOrchestrator.
                            When supplied, Athena routing is skipped.
        """
        decision = route_decision if route_decision is not None else self._route(context)
        messages = self._build_messages(context)
        return llm_orchestrator.execute(
            decision=decision,
            messages=messages,
            context=context,
        )

    def stream(
        self,
        context: PromptContext,
        route_decision: RouteDecision | None = None,
    ):
        """
        Streaming LLM call.  Yields str chunks.

        Args:
            context: Full prompt context built by ContextBuilder.
            route_decision: Pre-computed RouteDecision from AthenaOrchestrator.
                            When supplied, Athena routing is skipped.
        """
        decision = route_decision if route_decision is not None else self._route(context)
        messages = self._build_messages(context)
        yield from llm_orchestrator.execute_stream(
            decision=decision,
            messages=messages,
            context=context,
        )


llm = LLMService()
