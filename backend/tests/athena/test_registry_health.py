from app.athena.registry import model_registry


def test_all_models_enabled():

    assert len(model_registry.enabled()) == 6


def test_all_models_healthy():

    assert len(model_registry.healthy()) == 6
