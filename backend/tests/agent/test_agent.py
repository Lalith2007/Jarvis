from app.agent.service import agent


def test_agent_search():
    result = agent.run("Find README")

    assert result.tool_used
    assert result.tool_result is not None
    assert result.tool_result.success
