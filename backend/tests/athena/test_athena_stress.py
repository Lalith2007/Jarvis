import time
import uuid
from typing import List

from app.agents.hermes.models import PromptContext
from app.athena.engines.orchestrator import athena
from app.mission.models import Mission
from app.mission.builder import mission_graph_builder


def generate_prompts() -> List[str]:
    base_prompts = [
        "Find the README file in the backend directory.",
        "Refactor the User API to use FastAPI dependencies.",
        "Write a Python script to scrape a website.",
        "Hello, how are you today?",
        "What is the average latency of the system?",
        "rm -rf /",
        "Deploy the application to AWS.",
        "Explain quantum physics to a 5 year old.",
        "Organize my files in the downloads folder.",
        "Create a dashboard for monitoring metrics."
    ]
    # Replicate to get 500 prompts
    return base_prompts * 50


def test_athena_stress():
    prompts = generate_prompts()
    
    start_time = time.time()
    
    confidences = []
    capabilities_generated = 0
    memory_plans = 0
    policy_approved = 0
    graphs_generated = 0
    
    for idx, prompt in enumerate(prompts):
        context = PromptContext(system_prompt="sys", user_query=prompt)
        
        # Test Athena Analysis Latency
        decision = athena.analyze(context)
        
        confidences.append(decision.confidence)
        
        if len(decision.recommended_capabilities) > 0:
            capabilities_generated += 1
            
        if decision.memory_plan:
            memory_plans += 1
            
        # Policy is implicitly approved if capabilities exist, since policy wipe capabilities on failure
        # In our current logic, we just check if risk is evaluated
        if decision.risk_level:
            policy_approved += 1
            
        # Test Graph Generation Correctness
        mission = Mission(
            id=str(uuid.uuid4()),
            execution_id=str(uuid.uuid4()),
            goal=prompt
        )
        graph = mission_graph_builder.build(mission)
        if len(graph.nodes) > 0:
            graphs_generated += 1

    total_time = time.time() - start_time
    avg_latency = (total_time / len(prompts)) * 1000
    
    # Assertions to ensure stress test passed expectations
    assert len(confidences) == 500
    assert avg_latency < 50.0  # Should be extremely fast, < 50ms per decision
    
    # Check distributions
    high_conf = sum(1 for c in confidences if c >= 0.80)
    low_conf = sum(1 for c in confidences if c < 0.80)
    assert high_conf >= 250  # At least half should be highly confident heuristically
    
    assert capabilities_generated >= 300
    assert memory_plans == 500
    assert graphs_generated >= 300
    
    print(f"Stress test completed in {total_time:.2f}s (Avg: {avg_latency:.2f}ms/decision)")
