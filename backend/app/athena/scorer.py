from app.agents.hermes.models import PromptContext
from app.athena.intent import intent_engine
from app.athena.models import (
    ModelRecommendation,
    ModelType,
)
from app.athena.registry import model_registry


class AthenaScorer:
    """
    Athena Recommendation Engine.

    Produces a ranked list of model recommendations
    based on:

        • User Intent
        • Model Capabilities
        • Model Health
        • Static Priority (tie-breaker)

    The scorer NEVER decides routing.
    """

    HEALTH_BONUS = 25

    MODEL_PRIORITY = {
        ModelType.GPT_OSS_120B: 5,
        ModelType.DEEPSEEK: 4,
        ModelType.NEMOTRON: 3,
        ModelType.MINIMAX: 2,
        ModelType.LLAMA31: 1,
    }

    def score(
        self,
        context: PromptContext,
    ) -> list[ModelRecommendation]:

        intent_result = intent_engine.detect(context)

        recommendations: list[ModelRecommendation] = []

        for model, info in model_registry.enabled().items():

            profile = info.profile

            total_score = 0.0

            reasons: list[str] = []

            for intent in intent_result.intents:

                capability = profile.capabilities.get(
                    intent.capability,
                    0,
                )

                contribution = (
                    capability
                    * intent.score
                    * intent.confidence
                ) / 100.0

                total_score += contribution

                if contribution > 0:
                    reasons.append(
                        (
                            f"{intent.capability.value}"
                            f" ({capability})"
                            f" -> +{contribution:.1f}"
                        )
                    )

            if info.healthy:
                total_score += self.HEALTH_BONUS
                reasons.append(
                    f"Healthy +{self.HEALTH_BONUS}"
                )

            recommendations.append(
                ModelRecommendation(
                    model=model,
                    score=round(total_score, 2),
                    confidence=None,
                    estimated_cost=None,
                    estimated_latency=None,
                    healthy=info.healthy,
                    reasons=reasons,
                )
            )

        recommendations.sort(
            key=lambda recommendation: (
                recommendation.score,
                self.MODEL_PRIORITY.get(
                    recommendation.model,
                    0,
                ),
            ),
            reverse=True,
        )

        return recommendations


scorer = AthenaScorer()
