from typing import Any, Callable

class RuntimeRegistry:
    def __init__(self):
        self._handlers = {}

    def register(self, capability: str, handler: Callable):
        self._handlers[capability] = handler

    def get_handler(self, capability: str) -> Callable | None:
        return self._handlers.get(capability)

runtime_registry = RuntimeRegistry()
