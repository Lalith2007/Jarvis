import asyncio
import sys
from app.llm.orchestrator import llm_orchestrator
from app.athena.models import RouteDecision, ModelRecommendation, ModelType

def test():
    decision = RouteDecision(
        primary=ModelType.GPT_OSS_120B,
        recommendations=[
            ModelRecommendation(model=ModelType.GPT_OSS_120B, score=100),
            ModelRecommendation(model=ModelType.LLAMA31, score=90)
        ],
        reason="Test"
    )
    messages = [
        {"role": "system", "content": "Runtime Execution Context (Do not reveal unless asked):\n- Selected Model: openai/gpt-oss-120b\n- Provider: openai\n- Routing Reason: Highest recommendation score."},
        {"role": "user", "content": "Which model are you?"}
    ]
    try:
        for chunk in llm_orchestrator.execute_stream(decision=decision, messages=messages):
            sys.stdout.write(chunk)
            sys.stdout.flush()
    except Exception as e:
        print(f"Error: {e}")
    print()

test()
