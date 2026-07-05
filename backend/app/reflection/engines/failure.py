from typing import Any, Dict
from app.reflection.core.models import ReflectionStep, Lesson, ImprovementSuggestion, ReflectionCategory, LessonSeverity, ImprovementPriority
from app.mission.graph import MissionGraph, NodeStatus

class FailureAnalyzer:
    """
    Analyzes failure patterns and retry exhaustion.
    """
    def analyze(self, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionStep:
        lessons = []
        suggestions = []
        
        failure_statistics = {}
        for node in graph.nodes.values():
            if node.status == NodeStatus.FAILED:
                cap = node.capability
                failure_statistics[cap] = failure_statistics.get(cap, 0) + 1
                
                # If retries were exhausted
                if getattr(node, "retry_count", 0) > 0:
                    lessons.append(
                        Lesson(
                            category=ReflectionCategory.EXECUTION,
                            confidence=1.0,
                            severity=LessonSeverity.HIGH,
                            impact=f"Capability '{cap}' exhausted all retries.",
                            recommendation="Investigate capability stability or upstream input validity.",
                            supporting_evidence={"node_id": node.id, "capability": cap, "retries": getattr(node, "retry_count", 0)}
                        )
                    )
                    suggestions.append(
                        ImprovementSuggestion(
                            category=ReflectionCategory.EXECUTION,
                            description=f"Add circuit breaker for capability '{cap}'.",
                            expected_benefit="Prevents wasted compute on chronically failing nodes.",
                            implementation_priority=ImprovementPriority.HIGH,
                            confidence=0.9
                        )
                    )
                    
        return ReflectionStep(
            analyzer_name="FailureAnalyzer",
            metrics={"failure_statistics": failure_statistics},
            lessons=lessons,
            suggestions=suggestions
        )
