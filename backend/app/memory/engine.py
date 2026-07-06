import time
from typing import List, Optional

from app.memory.core.models import (
    MemoryRecord,
    MemoryQuery,
    MemorySearchResult,
    MemoryWriteResult,
    MemoryReadResult,
    MemoryStatistics,
)
from app.memory.storage.base import MemoryStorage
from app.memory.storage.local import LocalMemoryStorage
from app.memory.pipeline.analyzer import QueryAnalyzer
from app.memory.pipeline.retriever import CandidateRetriever
from app.memory.pipeline.filter import MemoryFilter
from app.memory.pipeline.ranker import MemoryRanker
from app.memory.pipeline.deduplicator import Deduplicator
from app.memory.pipeline.summarizer import Summarizer

from app.platform.publisher import EventPublisher


class MemoryEngine:
    """
    The Single Gateway for JARVIS Memory operations.
    Fully deterministic, heuristic-based, thread-safe.
    """

    def __init__(self, storage: Optional[MemoryStorage] = None):
        self.storage = storage or LocalMemoryStorage()

    def store(self, record: MemoryRecord) -> MemoryWriteResult:
        try:
            self.storage.store(record)
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryStored",
                payload={"memory_id": record.memory_id}
            )
            return MemoryWriteResult(memory_id=record.memory_id, status="success", action="created")
        except Exception as e:
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryWriteRejected",
                payload={"memory_id": record.memory_id, "error": str(e)}
            )
            raise

    def update(self, record: MemoryRecord) -> MemoryWriteResult:
        try:
            self.storage.update(record)
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryUpdated",
                payload={"memory_id": record.memory_id}
            )
            return MemoryWriteResult(memory_id=record.memory_id, status="success", action="updated")
        except Exception as e:
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryWriteRejected",
                payload={"memory_id": record.memory_id, "error": str(e)}
            )
            raise

    def retrieve(self, memory_id: str) -> MemoryReadResult:
        record = self.storage.retrieve(memory_id)
        if record:
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryRetrieved",
                payload={"memory_id": memory_id, "found": True}
            )
            return MemoryReadResult(memory_id=memory_id, record=record, found=True)
        else:
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryRetrieved",
                payload={"memory_id": memory_id, "found": False}
            )
            return MemoryReadResult(memory_id=memory_id, record=None, found=False)

    def delete(self, memory_id: str) -> bool:
        deleted = self.storage.delete(memory_id)
        if deleted:
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryDeleted",
                payload={"memory_id": memory_id}
            )
        return deleted

    def search(self, query: MemoryQuery) -> MemorySearchResult:
        start_time = time.perf_counter()

        # 1. Analyze
        keywords, implicit_tags = QueryAnalyzer.analyze(query)

        # 2. Retrieve candidates
        candidates = CandidateRetriever.retrieve(self.storage, query)
        total_eval = len(candidates)

        # 3. Filter
        filtered = MemoryFilter.apply(candidates, query)

        # 4. Rank
        ranked = MemoryRanker.rank(filtered, keywords, implicit_tags)

        # 5. Deduplicate
        deduped = Deduplicator.apply(ranked)

        # 6. Summarize (Paginate)
        final_results = Summarizer.apply(deduped, query.limit, query.offset)

        execution_time = (time.perf_counter() - start_time) * 1000

        result = MemorySearchResult(
            query=query,
            results=final_results,
            total_candidates_evaluated=total_eval,
            execution_time_ms=execution_time
        )

        EventPublisher.publish(
            subsystem="memory",
            event_type="MemorySearchCompleted",
            payload={
                "query": query.query,
                "total_results": len(final_results),
                "execution_time_ms": execution_time
            }
        )

        return result

    def summarize(self, query: MemoryQuery) -> str:
        """
        High-level abstraction for integrations requiring plain text context.
        """
        result = self.search(query)
        if not result.results:
            return "No relevant memories found."
            
        summary_lines = []
        for r in result.results:
            summary_lines.append(f"[{r.type.value.upper()}] {r.title or 'Memory'}: {r.content}")
            
        return "\n".join(summary_lines)

    def statistics(self) -> MemoryStatistics:
        return self.storage.statistics()


# Global Singleton Facade
memory_engine = MemoryEngine()
