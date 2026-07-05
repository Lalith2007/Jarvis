import json
import random
import time
import uuid

import pytest

from app.mission.graph import MissionGraph, MissionNode, NodeStatus, NodeType
from app.mission.registry import capability_registry
from app.mission.engine import graph_execution_manager

# Register mock capabilities for testing
def mock_success(node: MissionNode):
    time.sleep(0.01)
    return {"status": "success", "val": node.payload.get("val", 0) + 1}

def mock_fail(node: MissionNode):
    time.sleep(0.01)
    raise ValueError("Intentional failure")

def mock_timeout(node: MissionNode):
    time.sleep(0.5)
    return {"status": "timeout_mocked"}

capability_registry.register("test.success", mock_success)
capability_registry.register("test.fail", mock_fail)
capability_registry.register("test.timeout", mock_timeout)

@pytest.fixture
def base_graph():
    return MissionGraph(graph_id="test_graph")

def test_sequential_execution(base_graph):
    # A -> B -> C
    node_a = MissionNode(id="A", type=NodeType.TOOL, capability="test.success", payload={"val": 0})
    node_b = MissionNode(id="B", type=NodeType.TOOL, capability="test.success", dependencies=["A"])
    node_c = MissionNode(id="C", type=NodeType.TOOL, capability="test.success", dependencies=["B"])
    
    base_graph.nodes = {"A": node_a, "B": node_b, "C": node_c}
    
    result = graph_execution_manager.execute(base_graph, "test_mission")
    
    assert base_graph.nodes["A"].status == NodeStatus.COMPLETED
    assert base_graph.nodes["B"].status == NodeStatus.COMPLETED
    assert base_graph.nodes["C"].status == NodeStatus.COMPLETED
    
    assert base_graph.nodes["A"].result["val"] == 1
    assert base_graph.nodes["B"].result["val"] == 2
    assert base_graph.nodes["C"].result["val"] == 3
    assert base_graph.successful_nodes == 3

def test_parallel_execution(base_graph):
    # A -> B
    # A -> C
    # B,C -> D
    node_a = MissionNode(id="A", type=NodeType.TOOL, capability="test.success", payload={"val": 0})
    node_b = MissionNode(id="B", type=NodeType.TOOL, capability="test.success", dependencies=["A"])
    node_c = MissionNode(id="C", type=NodeType.TOOL, capability="test.success", dependencies=["A"])
    node_d = MissionNode(id="D", type=NodeType.TOOL, capability="test.success", dependencies=["B", "C"])
    
    base_graph.nodes = {"A": node_a, "B": node_b, "C": node_c, "D": node_d}
    
    result = graph_execution_manager.execute(base_graph, "test_mission")
    
    assert base_graph.nodes["D"].status == NodeStatus.COMPLETED
    # A=1, B=2, C=2, D gets val=2 and increments to 3
    assert base_graph.nodes["D"].result["val"] == 3
    assert base_graph.successful_nodes == 4

def test_failure_propagation(base_graph):
    # A -> B (fails) -> C
    node_a = MissionNode(id="A", type=NodeType.TOOL, capability="test.success")
    node_b = MissionNode(id="B", type=NodeType.TOOL, capability="test.fail", dependencies=["A"])
    node_c = MissionNode(id="C", type=NodeType.TOOL, capability="test.success", dependencies=["B"])
    
    base_graph.nodes = {"A": node_a, "B": node_b, "C": node_c}
    
    result = graph_execution_manager.execute(base_graph, "test_mission")
    
    assert base_graph.nodes["A"].status == NodeStatus.COMPLETED
    assert base_graph.nodes["B"].status == NodeStatus.FAILED
    assert base_graph.nodes["C"].status == NodeStatus.CANCELLED
    
    assert base_graph.failed_nodes == 1
    assert result is None

def test_retry_policy(base_graph):
    # Register a flakey capability
    attempts = 0
    def mock_flakey(node):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Flakey fail")
        return {"status": "finally_success"}
        
    capability_registry.register("test.flakey", mock_flakey)
    
    node = MissionNode(id="A", type=NodeType.TOOL, capability="test.flakey", retry_count=3)
    base_graph.nodes = {"A": node}
    
    result = graph_execution_manager.execute(base_graph, "test_mission")
    
    assert node.status == NodeStatus.COMPLETED
    assert node.result["status"] == "finally_success"
    assert attempts == 3

def test_serialization_round_trip(base_graph):
    node = MissionNode(id="A", type=NodeType.TOOL, capability="test.success")
    base_graph.nodes = {"A": node}
    
    # dict roundtrip
    d = base_graph.to_dict()
    assert d["graph_id"] == base_graph.graph_id
    reconstructed_dict = MissionGraph.from_dict(d)
    assert reconstructed_dict.nodes["A"].id == "A"
    
    # json roundtrip
    j = base_graph.to_json()
    reconstructed_json = MissionGraph.from_json(j)
    assert reconstructed_json.nodes["A"].capability == "test.success"

def test_100_node_stress_test(base_graph):
    # Build a random DAG with 100 nodes
    nodes = {}
    
    for i in range(100):
        node_id = f"node_{i}"
        
        # Pick 0-3 random dependencies from earlier nodes to ensure DAG
        deps = []
        if i > 0:
            num_deps = random.randint(0, min(i, 3))
            if num_deps > 0:
                deps = random.sample([f"node_{j}" for j in range(i)], num_deps)
                
        node = MissionNode(
            id=node_id, 
            type=NodeType.TOOL, 
            capability="test.success",
            dependencies=deps
        )
        nodes[node_id] = node
        
    base_graph.nodes = nodes
    
    graph_execution_manager.execute(base_graph, "test_stress")
    
    assert base_graph.successful_nodes == 100
    for node in base_graph.nodes.values():
        assert node.status == NodeStatus.COMPLETED

