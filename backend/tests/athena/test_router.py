from app.agents.hermes.models import PromptContext
from app.athena.models import ModelType
from app.athena.router import athena


def make_context(query: str) -> PromptContext:
    return PromptContext(
        system_prompt="",
        user_query=query,
    )


def test_code_routes_to_deepseek():

    decision = athena.route(
        make_context(
            "Help me debug my Python code"
        )
    )

    assert decision.primary == ModelType.DEEPSEEK

    assert (
        decision.recommendations[0].model
        == ModelType.DEEPSEEK
    )

    # Ensure at least one additional recommendation exists.
    # The exact fallback order may evolve as new models are added.
    assert len(decision.recommendations) >= 2


def test_general_routes_to_gpt_oss():

    decision = athena.route(
        make_context(
            "How are you?"
        )
    )

    assert decision.primary == ModelType.GPT_OSS_120B

    assert (
        decision.recommendations[0].model
        == ModelType.GPT_OSS_120B
    )

    assert len(decision.recommendations) >= 2
