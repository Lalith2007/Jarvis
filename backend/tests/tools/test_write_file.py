from app.tools import tool_registry
from app.tools.models import ToolCall


def test_write_file(tmp_path):
    file = tmp_path / "hello.txt"

    result = tool_registry.execute(
        ToolCall(
            name="write_file",
            arguments={
                "path": str(file),
                "content": "Hello JARVIS!",
            },
        )
    )

    assert result.success
    assert file.exists()
    assert file.read_text() == "Hello JARVIS!"
