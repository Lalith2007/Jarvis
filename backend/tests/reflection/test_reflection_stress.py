import pytest
import time
import random
from app.mission.graph import MissionGraph, MissionNode, NodeStatus, NodeType
from app.reflection.orchestrator import reflection_orchestrator
from app.reflection.core.models import ReflectionResult

def generate_random_graph(nodes_count=20):
    graph = MissionGraph(graph_id="g1")
    for i in range(nodes_count):
        n = MissionNode(id=f"n{i}", type=NodeType.TOOL, capability=f"cap.{i%3}")
        n.status = NodeStatus.COMPLETED if random.random() > 0.1 else NodeStatus.FAILED
        n.execution_time_ms = random.uniform(10, 200)
        n.retry_count = 1 if n.status == NodeStatus.FAILED else 0
        graph.nodes[n.id] = n
        
    graph.successful_nodes = sum(1 for n in graph.nodes.values() if n.status == NodeStatus.COMPLETED)
    graph.failed_nodes = nodes_count - graph.successful_nodes
    graph.graph_duration_ms = sum(n.execution_time_ms for n in graph.nodes.values()) * 0.8  # Simulating some parallelism
    return graph

def test_reflection_stress():
    start_time = time.time()
    
    results = []
    # Reflect 1000 synthetic missions
    for i in range(1000):
        graph = generate_random_graph(20)
        res = reflection_orchestrator.reflect(
            mission_id=f"m{i}",
            session_id="s1",
            mission_dict={"metadata": {"latency_budget_ms": 2000.0}},
            graph=graph
        )
        assert res is not None
        results.append(res)
        
    end_time = time.time()
    total_duration = end_time - start_time
    avg_latency = (total_duration / 1000) * 1000
    
    # Must be bounded latency (expected < 10ms per reflection)
    assert avg_latency < 10.0
    
    # Verify serialization integrity on one
    r1 = results[0]
    json_data = r1.to_json()
    r1_reconstructed = ReflectionResult.from_json(json_data)
    assert r1.mission_id == r1_reconstructed.mission_id
    assert r1.metrics.mission_duration_ms == r1_reconstructed.metrics.mission_duration_ms
