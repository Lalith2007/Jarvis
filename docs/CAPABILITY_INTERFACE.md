# Capability Interface Contract

In the Mission Execution Graph architecture, the underlying scheduling engine does not understand logic. It delegates execution to the `CapabilityManager`, which acts as a router pointing to registered capability implementations.

## `CapabilityRegistry`

The registry (`app/mission/registry.py`) decouples hardcoded nodes from executable functions.

```python
CapabilityExecutor = Callable[[MissionNode], Any]
```

Subsystems register their execution boundary functions into this global registry:
```python
capability_registry.register("planner.plan", execute_planner)
capability_registry.register("executor.execute", execute_tool)
```

## Creating a Capability Plugin

To implement a new capability that can be referenced natively inside the Graph:

1. Define a boundary function taking `MissionNode` as an argument.
2. Read required context (such as mission goals or prior dependency results) exclusively from `node.payload` or `node.metadata`.
3. Interact with your specialized subsystem.
4. Return a structured object or dictionary. The `GraphExecutionManager` handles injecting this returned value into downstream dependent payloads.

### Example Plugin Contract
```python
def execute_my_capability(node: MissionNode) -> Any:
    # 1. Read Payload dependencies
    previous_result = node.payload.get("planner.plan")
    mission_id = node.payload.get("execution_id")
    
    # 2. Subsystem logic execution
    import my_subsystem
    output = my_subsystem.run(previous_result)
    
    # 3. Return primitive or object
    return {"status": "success", "data": output}
```

The strictness of this pattern ensures execution engine isolation, permitting future distributed scaling, serverless workers, or pure-event microservice decoupling without mutating the core DAG runner.
