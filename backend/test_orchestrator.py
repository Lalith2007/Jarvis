import asyncio
import sys
from app.llm.orchestrator import llm_orchestrator
from app.athena.models import RouteDecision, ModelRecommendation, ModelType
from app.agents.hermes.models import PromptContext
from datetime import datetime

def test():
    decision = RouteDecision(
        primary=ModelType.GPT_OSS_120B,
        recommendations=[
            ModelRecommendation(model=ModelType.GPT_OSS_120B, score=100),
            ModelRecommendation(model=ModelType.LLAMA31, score=90)
        ],
        reason="Test fallback"
    )
    context = PromptContext(
        system_prompt="",
        user_query="Which model are you?",
        metadata={"session_id": "123"}
    )
    messages = [
        {"role": "user", "content": "Which model are you?"}
    ]
    try:
        for chunk in llm_orchestrator.execute_stream(decision=decision, messages=messages, context=context):
            sys.stdout.write(chunk)
            sys.stdout.flush()
    except Exception as e:
        print(f"Error: {e}")
    print()

test()
