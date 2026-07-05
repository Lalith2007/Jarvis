# Model Routing

The `ModelRankingEngine` assigns models to tasks dynamically based on:
1. **Complexity**: Heavy tasks default to `GPT_OSS_120B` or `LLAMA31`. Simple tasks default to `MINIMAX`.
2. **Latency Budget**: If the latency budget is tight, it prefers `DEEPSEEK`.

Models are outputted as a ranked list of `ModelRecommendation` objects inside the `AthenaDecision`. The Execution layer is responsible for falling back to lower-ranked models if the primary model fails or times out.
