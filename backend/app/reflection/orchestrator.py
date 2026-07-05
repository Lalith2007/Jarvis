import logging
from typing import Any, Dict
from app.platform.publisher import EventPublisher
from app.mission.graph import MissionGraph
from app.reflection.core.models import ReflectionResult, ReflectionMetrics, MissionSummary
from app.reflection.engines import (
    MissionAnalyzer, PerformanceAnalyzer, FailureAnalyzer, 
    ResourceAnalyzer, CapabilityAnalyzer, LearningEngine
)

logger = logging.getLogger(__name__)

class ReflectionOrchestrator:
    """
    Coordinates the reflection pipeline. Always runs strictly read-only and swallows exceptions.
    """
    def __init__(self):
        self.mission_analyzer = MissionAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.failure_analyzer = FailureAnalyzer()
        self.resource_analyzer = ResourceAnalyzer()
        self.capability_analyzer = CapabilityAnalyzer()
        self.learning_engine = LearningEngine()

    def reflect(self, mission_id: str, session_id: str, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionResult | None:
        try:
            EventPublisher.publish(
                subsystem="reflection",
                event_type="ReflectionStarted",
                mission_id=mission_id,
                session_id=session_id
            )
            
            steps = []
            
            # Deterministic, sequential pipeline
            analyzers = [
                self.mission_analyzer,
                self.performance_analyzer,
                self.failure_analyzer,
                self.resource_analyzer,
                self.capability_analyzer
            ]
            
            for analyzer in analyzers:
                step = analyzer.analyze(mission_dict, graph)
                steps.append(step)
                
            learning_step = self.learning_engine.analyze(mission_dict, graph, steps)
            steps.append(learning_step)
            
            # Aggregate all lessons and suggestions
            all_lessons = []
            all_suggestions = []
            metrics_dict = {}
            
            for step in steps:
                for lesson in step.lessons:
                    all_lessons.append(lesson)
                    EventPublisher.publish(
                        subsystem="reflection",
                        event_type="LessonGenerated",
                        mission_id=mission_id,
                        session_id=session_id,
                        payload=lesson.model_dump()
                    )
                    
                for suggestion in step.suggestions:
                    all_suggestions.append(suggestion)
                    EventPublisher.publish(
                        subsystem="reflection",
                        event_type="SuggestionGenerated",
                        mission_id=mission_id,
                        session_id=session_id,
                        payload=suggestion.model_dump()
                    )
                
                metrics_dict.update(step.metrics)
                
            metrics = ReflectionMetrics(**metrics_dict)
            summary = MissionSummary(
                mission_id=mission_id,
                session_id=session_id,
                success=graph.failed_nodes == 0,
                total_nodes=len(graph.nodes),
                successful_nodes=graph.successful_nodes,
                failed_nodes=graph.failed_nodes
            )
            
            result = ReflectionResult(
                mission_id=mission_id,
                summary=summary,
                metrics=metrics,
                steps=steps,
                lessons=all_lessons,
                suggestions=all_suggestions
            )
            
            EventPublisher.publish(
                subsystem="reflection",
                event_type="ReflectionCompleted",
                mission_id=mission_id,
                session_id=session_id
            )
            return result
            
        except Exception as e:
            logger.error(f"Reflection failed for mission {mission_id}: {e}", exc_info=True)
            EventPublisher.publish(
                subsystem="reflection",
                event_type="ReflectionFailed",
                mission_id=mission_id,
                session_id=session_id,
                severity="error",
                payload={"error": str(e)}
            )
            return None

reflection_orchestrator = ReflectionOrchestrator()
