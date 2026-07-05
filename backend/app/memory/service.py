from app.memory.conversation.service import conversation
from app.memory.vault.service import vault
from app.query.models import ProcessedQuery


class MemoryService:
    """
    Unified entry point for the Memory subsystem.

    Exposes a stable API while delegating to the
    appropriate internal services.
    """

    def __init__(self):
        self.conversation = conversation
        self.vault = vault

    # --------------------------------------------------
    # Vault
    # --------------------------------------------------

    def build(self):
        return self.vault.build()

    def notes(self):
        return self.vault.notes()

    def read(
        self,
        path: str,
    ):
        return self.vault.read(path)

    def search(
        self,
        query: ProcessedQuery,
        limit: int = 5,
    ):
        results = self.vault.search(
            query=query,
            limit=limit,
        )
        
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="memory",
            event_type="MemoryRetrieved",
            payload={"query": query.model_dump() if hasattr(query, "model_dump") else {}, "results_count": len(results)}
        )
        
        return results


memory = MemoryService()
