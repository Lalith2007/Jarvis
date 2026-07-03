"""
Backward compatibility.

Existing code imports:

    from app.memory.memory_service import memory

Internally we now expose:

    app.memory.service

This wrapper prevents older imports from breaking.
"""

from app.memory.service import memory

__all__ = ["memory"]
