from app.agents.hermes.models import PromptContext
from app.athena.intent import intent_engine
from app.athena.models import (
    ModelRecommendation,
    ModelType,
)
from app.athena.registry import model_registry
from app.athena.task_analysis import (
    ContextRequirement,
    TaskComplexity,
)
from app.athena.task_analyzer import task_analyzer


class AthenaScorer:
    """
    Athena Recommendation Engine.

    Produces ranked model recommendations using:

        • User Intent
        • Model Capabilities
        • Task Analysis
        • Model Health
        • Static Priority

    This class never performs routing.
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

        intent = intent_engine.detect(context)

        analysis = task_analyzer.analyze(
            context=context,
            intent=intent,
        )

        recommendations: list[ModelRecommendation] = []

        for model, info in model_registry.enabled().items():

            profile = info.profile

            total_score = 0.0

            reasons: list[str] = []

            # ---------------------------------
            # Capability scoring
            # ---------------------------------

            for detected in intent.intents:

                capability_strength = profile.capabilities.get(
                    detected.capability,
                    0,
                )

                contribution = (
                    capability_strength
                    * detected.score
                    * detected.confidence
                ) / 100.0

                total_score += contribution

                if contribution > 0:
                    reasons.append(
                        (
                            f"{detected.capability.value}"
                            f" ({capability_strength})"
                            f" -> +{contribution:.1f}"
                        )
                    )

            # ---------------------------------
            # Context bonus
            # ---------------------------------

            if (
                analysis.context_requirement
                == ContextRequirement.VERY_LARGE
                and model == ModelType.MINIMAX
            ):
                total_score += 30
                reasons.append(
                    "Very large context +30"
                )

            elif (
                analysis.context_requirement
                == ContextRequirement.LARGE
                and model == ModelType.MINIMAX
            ):
                total_score += 15
                reasons.append(
                    "Large context +15"
                )

            # ---------------------------------
            # Complexity bonus
            # ---------------------------------

            if (
                analysis.complexity
                == TaskComplexity.EXPERT
                and model == ModelType.NEMOTRON
            ):
                total_score += 15
                reasons.append(
                    "Expert reasoning +15"
                )

            elif (
                analysis.complexity
                == TaskComplexity.COMPLEX
                and model == ModelType.NEMOTRON
            ):
                total_score += 8
                reasons.append(
                    "Complex planning +8"
                )

            # ---------------------------------
            # Tool usage
            # ---------------------------------

            if (
                analysis.requires_tools
                and model == ModelType.DEEPSEEK
            ):
                total_score += 10
                reasons.append(
                    "Tool execution +10"
                )

            # ---------------------------------
            # Memory
            # ---------------------------------

            if (
                analysis.requires_memory
                and model == ModelType.MINIMAX
            ):
                total_score += 8
                reasons.append(
                    "Memory retrieval +8"
                )

            # ---------------------------------
            # Health
            # ---------------------------------

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
