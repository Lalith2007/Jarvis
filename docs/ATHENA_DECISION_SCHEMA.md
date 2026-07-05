# Athena Decision Schema

The `AthenaDecision` object is the definitive output of the Intelligence layer. It is consumed by the `MissionGraphBuilder` to dynamically architect the graph.

```python
class AthenaDecision(BaseModel):
    intent: IntentClass
    task_type: str
    complexity: ComplexityClass
    estimated_cost: float
    estimated_latency: float
    confidence: float
    
    memory_plan: MemoryPlan
    execution_strategy: ExecutionStrategy
    recommended_capabilities: List[CapabilityRecommendation]
    recommended_models: List[ModelRecommendation]
    
    requires_parallel_execution: bool
    requires_reflection: bool
    requires_memory: bool
    requires_tools: bool
    
    risk_level: str
    reasoning_summary: str
    
    # Budgets enforced by Policy Engine
    token_budget: int
    latency_budget_ms: float
    cost_budget: float
    maximum_parallelism: int
    
    decision_trace: List[str]
```

## Sub-Schemas
- **CapabilityRecommendation**: Defines exactly what tools should execute, their priority, and whether they can run in parallel.
- **MemoryPlan**: Defines the memory strategy (Working, Semantic, Episodic) and sets retrieval token budgets.
