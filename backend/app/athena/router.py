from app.agents.hermes.models import PromptContext
from app.athena.models import RouteDecision
from app.athena.scorer import scorer


class Athena:
    """
    Athena Intelligence Layer.

    Responsible for producing a ranked list of model
    recommendations and selecting the primary model.

    Pipeline:

        User Query
            ↓
        Intent Engine
            ↓
        Recommendation Engine
            ↓
        Route Decision

    Future versions will support:

    • Cost-aware routing
    • Latency-aware routing
    • Health-aware routing
    • Context-aware routing
    • Multi-model execution
    • Learning from historical performance
    """

    def route(
        self,
        context: PromptContext,
    ) -> RouteDecision:

        recommendations = scorer.score(context)

        decision = RouteDecision(
            primary=recommendations[0].model,
            recommendations=recommendations,
            reason="Highest recommendation score.",
        )
        
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="athena",
            event_type="AthenaDecision",
            payload={"decision": decision.model_dump() if hasattr(decision, "model_dump") else {}}
        )

        return decision


athena = Athena()
