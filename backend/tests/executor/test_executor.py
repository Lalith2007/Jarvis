from pathlib import Path

from app.executor.service import executor
from app.planner.models import Plan


def test_executor():
    plan = Plan(
        use_tool=True,
        tool_name="list_directory",
        arguments={
            "path": str(Path.cwd()),
        },
    )

    result = executor.execute(plan)

    assert result.success
