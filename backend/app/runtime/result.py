from app.runtime.models import RuntimeResult

def create_success(output: str) -> RuntimeResult:
    return RuntimeResult(success=True, output=output)

def create_error(error: str) -> RuntimeResult:
    return RuntimeResult(success=False, error=error)
