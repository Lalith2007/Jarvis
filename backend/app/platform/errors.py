class JarvisError(Exception):
    """Base exception for canonical backend errors."""
    def __init__(self, message: str, error_code: str, recoverable: bool = False):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.recoverable = recoverable

class MissionFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message, "MISSION_FAILED", recoverable)

class AthenaFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message, "ATHENA_FAILED", recoverable)

class MemoryRetrievalFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message, "MEMORY_RETRIEVAL_FAILED", recoverable)

class PlanningFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message, "PLANNING_FAILED", recoverable)

class ExecutionFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message, "EXECUTION_FAILED", recoverable)

class StreamingFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__(message, "STREAMING_FAILED", recoverable)

class ProviderFailed(JarvisError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__(message, "PROVIDER_FAILED", recoverable)
