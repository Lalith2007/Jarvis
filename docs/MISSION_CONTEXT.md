# MissionContext Specification

The `MissionContext` is the canonical state object passed throughout the JARVIS execution pipeline. It replaces disparate arguments like `session_id` and `user_query` being passed individually.

## Schema Structure
```json
{
  "request_id": "uuid (Strictly enforced)",
  "session_id": "uuid",
  "mission": {
    "mission_id": "uuid",
    "status": "string (pending | running | completed | failed)"
  },
  "prompt_context": {
    "system_prompt": "string",
    "user_query": "string (Required field)",
    "conversation": "List[Message]",
    "knowledge": "List[Document]",
    "tool_results": "List[dict]",
    "metadata": "dict"
  },
  "execution": {
    "planner_result": "dict",
    "runtime_result": "dict"
  },
  "athena_decision": {
    "model_chosen": "string",
    "reasoning": "string"
  },
  "plan": null,
  "timing": {
    "start_time": "float",
    "end_time": "float"
  }
}
```

## Injection Rules
1. `MissionContext` is instantiated exactly once per request inside `Hermes.chat` or `Hermes.chat_stream`.
2. It must be explicitly passed as the first logical argument to `MissionController.run`, `Athena.route`, `Planner.plan`, and `Executor.execute`.
3. Subsystems append to their respective dictionaries (e.g., `execution` or `athena_decision`) without mutating the core `prompt_context`.
