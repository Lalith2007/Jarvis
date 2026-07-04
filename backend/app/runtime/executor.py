from app.runtime.models import RuntimeResult
from typing import Any

class RuntimeExecutor:
    def execute(self, handler, *args, **kwargs) -> RuntimeResult:
        try:
            output = handler(*args, **kwargs)
            return RuntimeResult(success=True, output=output)
        except Exception as e:
            return RuntimeResult(success=False, error=str(e))

runtime_executor = RuntimeExecutor()
