from app.runtime.models import RuntimeResult
import time
from typing import Any

class RuntimeExecutor:
    def execute(self, handler, *args, **kwargs) -> RuntimeResult:
        start_time = time.time()
        try:
            output = handler(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            return RuntimeResult(success=True, output=output, execution_time_ms=duration)
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return RuntimeResult(success=False, error=str(e), execution_time_ms=duration)

runtime_executor = RuntimeExecutor()
