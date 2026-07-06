from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.memory.core.models import MemoryRecord, MemoryStatistics


class MemoryStorage(ABC):
    """
    Abstract interface for JARVIS Memory persistence.
    """

    @abstractmethod
    def store(self, record: MemoryRecord) -> None:
        """Store a new memory record."""
        pass

    @abstractmethod
    def retrieve(self, memory_id: str) -> Optional[MemoryRecord]:
        """Retrieve a specific memory record by ID."""
        pass

    @abstractmethod
    def update(self, record: MemoryRecord) -> None:
        """Update an existing memory record."""
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory record. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def get_all(self) -> List[MemoryRecord]:
        """Retrieve all memory records for candidate generation."""
        pass

    @abstractmethod
    def statistics(self) -> MemoryStatistics:
        """Generate storage statistics."""
        pass
