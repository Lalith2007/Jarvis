from typing import Any, Dict
from app.reflection.core.models import ReflectionStep, Lesson, ImprovementSuggestion, ReflectionCategory, LessonSeverity, ImprovementPriority
from app.mission.graph import MissionGraph

class PerformanceAnalyzer:
    """
    Analyzes graph duration, bottlenecks, and parallelism.
    """
    def analyze(self, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionStep:
        lessons = []
        suggestions = []
        
        graph_duration = getattr(graph, "graph_duration_ms", 0.0)
        
        # Calculate theoretical minimum duration vs actual
        critical_path_ms = 0.0
        total_execution_ms = 0.0
        
        for node in graph.nodes.values():
            exec_time = getattr(node, "execution_time_ms", 0.0) or 0.0
            total_execution_ms += exec_time
            if exec_time > critical_path_ms:
                # Naive critical path tracking for deterministic heuristic
                critical_path_ms = exec_time
                
        parallelism_score = (total_execution_ms / graph_duration) if graph_duration > 0 else 1.0
        
        # Rule: Poor parallelism
        if parallelism_score < 1.1 and total_execution_ms > 1000.0 and len(graph.nodes) > 2:
            lessons.append(
                Lesson(
                    category=ReflectionCategory.PERFORMANCE,
                    confidence=0.8,
                    severity=LessonSeverity.MEDIUM,
                    impact="Graph execution is largely sequential, reducing throughput.",
                    recommendation="Review dependency graph to identify parallelizable tasks.",
                    supporting_evidence={"parallelism_score": parallelism_score, "nodes": len(graph.nodes)}
                )
            )
            suggestions.append(
                ImprovementSuggestion(
                    category=ReflectionCategory.PLANNING,
                    description="Optimize mission planner to reduce linear dependencies.",
                    expected_benefit="Lower mission completion latency.",
                    implementation_priority=ImprovementPriority.MEDIUM,
                    confidence=0.75
                )
            )
            
        return ReflectionStep(
            analyzer_name="PerformanceAnalyzer",
            metrics={
                "graph_duration_ms": graph_duration,
                "total_execution_ms": total_execution_ms,
                "parallelism_score": parallelism_score
            },
            lessons=lessons,
            suggestions=suggestions
        )
