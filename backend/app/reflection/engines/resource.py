from typing import Any, Dict
from app.reflection.core.models import ReflectionStep, Lesson, ImprovementSuggestion, ReflectionCategory, LessonSeverity, ImprovementPriority
from app.mission.graph import MissionGraph

class ResourceAnalyzer:
    """
    Analyzes resource constraints and budget usage.
    """
    def analyze(self, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionStep:
        lessons = []
        suggestions = []
        
        # In a real run, budget might be in mission metadata
        total_budget_ms = mission_dict.get("metadata", {}).get("latency_budget_ms", 0.0)
        graph_duration = getattr(graph, "graph_duration_ms", 0.0)
        
        budget_usage = 0.0
        if total_budget_ms > 0:
            budget_usage = (graph_duration / total_budget_ms) * 100.0
            
            if budget_usage > 90.0:
                lessons.append(
                    Lesson(
                        category=ReflectionCategory.RESOURCE_CONSUMPTION,
                        confidence=0.95,
                        severity=LessonSeverity.HIGH if budget_usage > 100.0 else LessonSeverity.MEDIUM,
                        impact=f"Mission consumed {budget_usage:.1f}% of allocated latency budget.",
                        recommendation="Optimize graph execution or increase Athena latency budget allocation.",
                        supporting_evidence={"budget_usage_percentage": budget_usage, "budget_ms": total_budget_ms, "duration_ms": graph_duration}
                    )
                )
        
        return ReflectionStep(
            analyzer_name="ResourceAnalyzer",
            metrics={"budget_usage_percentage": budget_usage},
            lessons=lessons,
            suggestions=suggestions
        )
