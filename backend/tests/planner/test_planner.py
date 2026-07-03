from app.planner.service import planner


def test_search_plan():
    plan = planner.plan(
        "Find README"
    )

    assert plan.use_tool
    assert plan.tool_name == "search_files"


def test_llm_plan():
    plan = planner.plan(
        "Explain reinforcement learning"
    )

    assert not plan.use_tool
