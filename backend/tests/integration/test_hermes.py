"""
Backward-compatibility test: hermes.chat() still works.
Updated for Sprint 11 (now returns tuple).
"""
import pytest

pytestmark = pytest.mark.live

from app.agents.hermes.service import hermes
from app.memory.conversation.service import conversation


def test_hermes_chat():
    response, session_id = hermes.chat("North")

    assert isinstance(response, str)
    assert len(response) > 0
    assert isinstance(session_id, str)

    history = conversation.history()

    assert len(history) >= 2
    assert history[-2]["role"] == "user"
    assert history[-1]["role"] == "assistant"
