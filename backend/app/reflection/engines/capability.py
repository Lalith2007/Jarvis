from typing import Any, Dict
from app.reflection.core.models import ReflectionStep, Lesson, ImprovementSuggestion, ReflectionCategory
from app.mission.graph import MissionGraph

class CapabilityAnalyzer:
    """
    Analyzes capability distribution across the mission.
    """
    def analyze(self, mission_dict: Dict[str, Any], graph: MissionGraph) -> ReflectionStep:
        breakdown = {}
        for node in graph.nodes.values():
            breakdown[node.capability] = breakdown.get(node.capability, 0) + 1
            
        return ReflectionStep(
            analyzer_name="CapabilityAnalyzer",
            metrics={"capability_breakdown": breakdown},
            lessons=[],
            suggestions=[]
        )
