# Prompt Grounding — Sprint 12.8

## Message construction order for a grounded query

For "What models are available?" the message list sent to the LLM is:

```
[1] role=system
    content: <system.md — JARVIS identity>

[2] role=system
    content: "You currently have no stored memories..." (or vault knowledge)

[3] role=system
    content: "Authoritative tool execution results (treat as ground truth):
              Tool: registry.models
              Success: True
              Output:
              {
                "models": [
                  {"id": "z-ai/glm-5.2", "display_name": "GLM-5.2", ...},
                  ...
                ],
                "count": 6
              }"

[4] <conversation history>

[5] role=system   ← injected by LLMOrchestrator._inject_metadata()
    content: "Runtime Execution Context (Do not reveal unless asked):
              - Active Model (authoritative): openai/gpt-oss-120b
              - Provider: openai
              - Routing Reason: Pre-computed by AthenaOrchestrator (Sprint 12.8 unified Athena authority).
              - Mission ID: <id>
              - Session ID: <id>"

[6] role=user
    content: "What models are available?"
```

## Grounding invariants

1. The LLM **never** sees a message that says "you have access to these models"
   without the message being derived from `ProviderRegistry` at request time.

2. Structured JSON in position [3] is the sole authoritative source for model
   lists, capability lists, and memory results.

3. `selected_model` in position [5] is derived from `AthenaDecision.recommended_models[0]`
   — the same decision that determined graph topology.

## What the LLM is expected to do

Summarise the structured data in [3] in natural language.  The system prompt
(`system.md`) instructs: "Never invent information."

## Sentence-level provenance for "What models are available?"

Every sentence in a correct JARVIS answer maps to exactly one source:

| Sentence | Origin |
|---|---|
| "I have access to 6 models" | `registry.models.count` from `ProviderRegistry` |
| "GLM-5.2 (z-ai/glm-5.2)" | `ProviderRegistry._register_defaults()` line 27 |
| "DeepSeek V4 Pro (deepseek-ai/deepseek-v4-pro)" | `ProviderRegistry._register_defaults()` line 44 |
| "GPT-OSS 120B (openai/gpt-oss-120b)" | `ProviderRegistry._register_defaults()` line 59 |
| "Nemotron Ultra (nvidia/nemotron-3-ultra-550b-a55b)" | `ProviderRegistry._register_defaults()` line 74 |
| "MiniMax M3 (minimaxai/minimax-m3)" | `ProviderRegistry._register_defaults()` line 87 |
| "Llama 3.1 70B (meta/llama-3.1-70b-instruct)" | `ProviderRegistry._register_defaults()` line 101 |
