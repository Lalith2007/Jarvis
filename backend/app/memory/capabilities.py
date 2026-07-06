import logging
from typing import Dict, Any, List

from app.capabilities.core.base import BaseCapability, CapabilityContext, CapabilityResult, CapabilityDiagnostics
from app.capabilities.core.models import CapabilityManifest, CapabilityConfig
from app.memory.engine import memory_engine
from app.memory.core.models import MemoryQuery, MemoryRecord, MemoryType, MemoryImportance

logger = logging.getLogger(__name__)


class MemoryReadCapability(BaseCapability):
    """
    Capability to retrieve memory for missions via MemoryEngine.
    """
    
    def __init__(self):
        manifest = CapabilityManifest(
            id="memory.retrieve",
            version="1.0.0",
            name="Memory Retrieval",
            description="Searches for context in Jarvis memory.",
            author="Jarvis System",
            category="Memory",
            parameters={
                "query": {"type": "string", "description": "Natural language query to search memory"},
                "limit": {"type": "integer", "description": "Max results to return (default: 5)"}
            },
            dependencies=[]
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 10.0

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        # Mission stores the user text under "goal"; older callers used "query".
        query_str = (
            context.runtime_state.get("goal")
            or context.runtime_state.get("query")
            or ""
        )
        limit = context.runtime_state.get("limit", 5)
        
        try:
            query = MemoryQuery(query=query_str, limit=limit)
            result = memory_engine.search(query)
            
            data = [r.to_dict() for r in result.results]
            
            return CapabilityResult(
                success=True,
                status="success",
                result={"results": data, "execution_time_ms": result.execution_time_ms},
                artifacts={"total_evaluated": result.total_candidates_evaluated}
            )
        except Exception as e:
            logger.error(f"MemoryReadCapability failed: {e}")
            return CapabilityResult(
                success=False,
                status="failed",
                result=None,
                errors=[str(e)]
            )


class MemoryWriteCapability(BaseCapability):
    """
    Capability to store new memories from missions via MemoryEngine.
    """
    
    def __init__(self):
        manifest = CapabilityManifest(
            id="memory.store",
            version="1.0.0",
            name="Memory Storage",
            description="Stores a new fact or context into Jarvis memory.",
            author="Jarvis System",
            category="Memory",
            parameters={
                "content": {"type": "string", "description": "The information to remember"},
                "title": {"type": "string", "description": "Short title for the memory"},
                "tags": {"type": "array", "description": "List of string tags"}
            },
            dependencies=[]
        )
        super().__init__(manifest, CapabilityConfig())
        
    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        if not context.runtime_state.get("content"):
            raise ValueError("content parameter is required")

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 10.0

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        content = context.runtime_state.get("content", "")
        title = context.runtime_state.get("title", "")
        tags = context.runtime_state.get("tags", [])
        
        try:
            record = MemoryRecord(
                content=content,
                title=title,
                tags=tags,
                source=context.mission_id if hasattr(context, "mission_id") else "mission"
            )
            write_result = memory_engine.store(record)
            
            return CapabilityResult(
                success=True,
                status="success",
                result=write_result.to_dict(),
                artifacts={}
            )
        except Exception as e:
            logger.error(f"MemoryWriteCapability failed: {e}")
            return CapabilityResult(
                success=False,
                status="failed",
                result=None,
                errors=[str(e)]
            )
