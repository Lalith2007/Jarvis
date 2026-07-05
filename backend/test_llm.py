import asyncio
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
    messages = [{"role": "user", "content": "Hello"}]
    try:
        for chunk in llm_orchestrator.execute_stream(decision=decision, messages=messages):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"Error: {e}")

test()
