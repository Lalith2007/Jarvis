from typing import List, Tuple

from app.athena.models import ComplexityClass, IntentClass, ModelRecommendation, ModelType


class ModelRankingEngine:
    """
    Deterministically ranks models based on complexity and intent.
    Returns (List[ModelRecommendation], confidence_score).

    All registered models stay routable — none are ever removed. When live
    health/latency data is available (ProviderRegistry.probe_health), the
    ranked list is re-ordered so responsive, low-latency models lead and
    slow/unresponsive ones sink to the end as fallbacks. When no probe has run
    (default), the ordering is unchanged (stable), so behaviour is unaffected.
    """

    def _health_order(
        self, recommendations: List[ModelRecommendation]
    ) -> List[ModelRecommendation]:
        from app.providers.registry import provider_registry

        by_id = {m.id: m for m in provider_registry.all()}

        def key(rec: ModelRecommendation):
            m = by_id.get(rec.model.value)
            if m is None:
                return (1, 0.0, -rec.score)  # unknown model: neutral
            healthy_rank = 0 if m.healthy else 1
            # Unprobed latency sorts as 0.0 so a fully-unprobed list keeps its
            # original (score-based) order via the stable sort.
            latency = m.avg_latency_ms if m.avg_latency_ms is not None else 0.0
            return (healthy_rank, latency, -rec.score)

        return sorted(recommendations, key=key)

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
            
        return self._health_order(recommendations), confidence
