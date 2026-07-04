from app.runtime.session import RuntimeSession
from app.runtime.dispatcher import runtime_dispatcher

class RuntimeManager:
    def create_session(self) -> RuntimeSession:
        return RuntimeSession()

runtime_manager = RuntimeManager()
