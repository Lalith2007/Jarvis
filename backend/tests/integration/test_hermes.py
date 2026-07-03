from app.agents.hermes.service import hermes
from app.memory.conversation.service import conversation


def test_hermes_chat():
    response = hermes.chat("North")

    assert isinstance(response, str)
    assert len(response) > 0

    history = conversation.history()

    assert len(history) >= 2
    assert history[-2]["role"] == "user"
    assert history[-1]["role"] == "assistant"
