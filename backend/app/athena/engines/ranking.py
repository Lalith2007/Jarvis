from typing import List, Tuple

from app.athena.models import ComplexityClass, IntentClass, ModelRecommendation, ModelType


class ModelRankingEngine:
    """
    Deterministically ranks models based on complexity and intent.
    Returns (List[ModelRecommendation], confidence_score).

    All registered models stay routable — slow models are waited on (see
    LLM_TIMEOUT), never disabled.
    """

    def evaluate(self, intent: IntentClass, complexity: ComplexityClass, risk: str) -> Tuple[List[ModelRecommendation], float]:
        recommendations = []
        confidence = 0.90
        
        # Heavy reasoning tasks
        if complexity in [ComplexityClass.expert, ComplexityClass.high] or intent in [IntentClass.coding, IntentClass.planning]:
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.GPT_OSS_120B,
                    score=0.98,
                    reason="Highest reasoning capability for complex logic.",
                    estimated_latency=3500.0,
                    estimated_cost=0.03
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.LLAMA31,
                    score=0.92,
                    reason="Strong alternative for complex logic.",
                    estimated_latency=2500.0,
                    estimated_cost=0.015
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.NEMOTRON,
                    score=0.88,
                    reason="Good fallback for heavy logic.",
                    estimated_latency=2000.0,
                    estimated_cost=0.01
                )
            )
        # Fast tasks
        elif complexity in [ComplexityClass.trivial, ComplexityClass.low] or intent in [IntentClass.conversation, IntentClass.summarization]:
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.MINIMAX,
                    score=0.95,
                    reason="Optimal for fast, simple responses.",
                    estimated_latency=500.0,
                    estimated_cost=0.001
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.DEEPSEEK,
                    score=0.90,
                    reason="Good balance of speed and capability.",
                    estimated_latency=800.0,
                    estimated_cost=0.002
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.GLM_52,
                    score=0.85,
                    reason="Fallback for fast responses.",
                    estimated_latency=600.0,
                    estimated_cost=0.0015
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.NEMOTRON,
                    score=0.82,
                    reason="Reliable general fallback.",
                    estimated_latency=2000.0,
                    estimated_cost=0.01
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.LLAMA31,
                    score=0.80,
                    reason="Reliable general fallback.",
                    estimated_latency=1500.0,
                    estimated_cost=0.01
                )
            )
        # General purpose
        else:
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.LLAMA31,
                    score=0.95,
                    reason="Excellent general purpose reasoning.",
                    estimated_latency=1500.0,
                    estimated_cost=0.01
                )
            )
            recommendations.append(
                ModelRecommendation(
                    model=ModelType.DEEPSEEK,
                    score=0.90,
                    reason="Fast general purpose fallback.",
                    estimated_latency=1000.0,
                    estimated_cost=0.005
                )
            )
            
        return recommendations, confidence
