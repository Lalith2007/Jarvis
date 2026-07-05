from typing import Any, Dict
from app.reflection.core.models import ReflectionStep, Lesson, ImprovementSuggestion, ReflectionCategory, LessonSeverity, ImprovementPriority
from app.mission.graph import MissionGraph

class MissionAnalyzer:
    """
    Analyzes overall mission success, structure, and basic topology.
    """
    def analyze(self, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionStep:
        lessons = []
        suggestions = []
        
        total_nodes = len(graph.nodes)
        success_rate = (graph.successful_nodes / total_nodes) if total_nodes > 0 else 0.0
        
        # Rule 1: High failure rate
        if total_nodes > 0 and success_rate < 0.5:
            lessons.append(
                Lesson(
                    category=ReflectionCategory.RELIABILITY,
                    confidence=0.9,
                    severity=LessonSeverity.HIGH,
                    impact="Mission success rate is below 50%.",
                    recommendation="Review capability robustness and graph dependencies.",
                    supporting_evidence={"success_rate": success_rate, "total_nodes": total_nodes}
                )
            )
            suggestions.append(
                ImprovementSuggestion(
                    category=ReflectionCategory.RELIABILITY,
                    description="Implement fallback paths for high-failure nodes.",
                    expected_benefit="Increased mission resilience and completion rate.",
                    implementation_priority=ImprovementPriority.HIGH,
                    confidence=0.85
                )
            )
            
        return ReflectionStep(
            analyzer_name="MissionAnalyzer",
            metrics={
                "total_nodes": total_nodes,
                "successful_nodes": graph.successful_nodes,
                "failed_nodes": graph.failed_nodes,
                "success_rate": success_rate
            },
            lessons=lessons,
            suggestions=suggestions
        )
