from app.athena.models import ModelType
from app.athena.registry import model_registry


def test_registry_contains_models():
    models = model_registry.all()

    assert ModelType.DEEPSEEK in models
    assert ModelType.NEMOTRON in models
    assert ModelType.MINIMAX in models
    assert ModelType.GPT_OSS_120B in models
    assert ModelType.LLAMA31 in models
