import pytest
from app.mission.graph import MissionGraph, MissionNode, NodeStatus, NodeType
from app.reflection.engines.mission import MissionAnalyzer
from app.reflection.engines.performance import PerformanceAnalyzer
from app.reflection.engines.failure import FailureAnalyzer
from app.reflection.engines.resource import ResourceAnalyzer
from app.reflection.engines.capability import CapabilityAnalyzer
from app.reflection.core.models import ReflectionCategory

@pytest.fixture
def sample_graph():
    graph = MissionGraph(graph_id="g1")
    n1 = MissionNode(id="n1", type=NodeType.TOOL, capability="test.c1")
    n1.status = NodeStatus.COMPLETED
    n1.execution_time_ms = 100
    
    n2 = MissionNode(id="n2", type=NodeType.TOOL, capability="test.c1")
    n2.status = NodeStatus.COMPLETED
    n2.execution_time_ms = 200
    
    n3 = MissionNode(id="n3", type=NodeType.TOOL, capability="test.c2")
    n3.status = NodeStatus.FAILED
    n3.execution_time_ms = 50
    n3.retry_count = 3
    
    graph.nodes = {"n1": n1, "n2": n2, "n3": n3}
    graph.successful_nodes = 2
    graph.failed_nodes = 1
    graph.graph_duration_ms = 250
    return graph

def test_mission_analyzer(sample_graph):
    analyzer = MissionAnalyzer()
    step = analyzer.analyze({}, sample_graph)
    
    assert step.metrics["total_nodes"] == 3
    assert step.metrics["success_rate"] == 2/3

def test_mission_analyzer_high_failure(sample_graph):
    sample_graph.successful_nodes = 1
    sample_graph.failed_nodes = 2
    
    analyzer = MissionAnalyzer()
    step = analyzer.analyze({}, sample_graph)
    
    assert len(step.lessons) == 1
    assert step.lessons[0].category == ReflectionCategory.RELIABILITY

def test_performance_analyzer(sample_graph):
    analyzer = PerformanceAnalyzer()
    step = analyzer.analyze({}, sample_graph)
    
    assert step.metrics["graph_duration_ms"] == 250
    assert step.metrics["total_execution_ms"] == 350
    assert step.metrics["parallelism_score"] == 350 / 250

def test_failure_analyzer(sample_graph):
    analyzer = FailureAnalyzer()
    step = analyzer.analyze({}, sample_graph)
    
    assert "test.c2" in step.metrics["failure_statistics"]
    assert step.metrics["failure_statistics"]["test.c2"] == 1
    assert len(step.lessons) == 1
    assert step.lessons[0].category == ReflectionCategory.EXECUTION

def test_capability_analyzer(sample_graph):
    analyzer = CapabilityAnalyzer()
    step = analyzer.analyze({}, sample_graph)
    
    breakdown = step.metrics["capability_breakdown"]
    assert breakdown["test.c1"] == 2
    assert breakdown["test.c2"] == 1
