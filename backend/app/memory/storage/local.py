import json
import os
import threading
from typing import List, Optional, Dict, Any

from app.memory.core.models import MemoryRecord, MemoryStatistics, MemoryType, MemoryImportance
from app.memory.storage.base import MemoryStorage
from app.config.settings import settings, BASE_DIR


class LocalMemoryStorage(MemoryStorage):
    """
    Deterministic, thread-safe JSON-backed storage for JARVIS Memory.
    """

    def __init__(self, file_path: Optional[str] = None):
        self._lock = threading.RLock()
        self._file_path = file_path or os.path.join(BASE_DIR, "data", "memory_store.json")
        self._memories: Dict[str, MemoryRecord] = {}
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        self._load()

    def _load(self):
        with self._lock:
            if not os.path.exists(self._file_path):
                self._save()
                return
                
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                for record_dict in data:
                    try:
                        record = MemoryRecord.from_dict(record_dict)
                        self._memories[record.memory_id] = record
                    except Exception as e:
                        # Skip corrupted individual records
                        pass
            except json.JSONDecodeError:
                # Recover gracefully from corrupted JSON
                self._memories = {}
                self._save()

    def _save(self):
        with self._lock:
            data = [record.to_dict() for record in self._memories.values()]
            # Write atomically using a temporary file
            tmp_path = f"{self._file_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, self._file_path)

    def store(self, record: MemoryRecord) -> None:
        with self._lock:
            self._memories[record.memory_id] = record
            self._save()

    def retrieve(self, memory_id: str) -> Optional[MemoryRecord]:
        with self._lock:
            return self._memories.get(memory_id)

    def update(self, record: MemoryRecord) -> None:
        with self._lock:
            if record.memory_id in self._memories:
                self._memories[record.memory_id] = record
                self._save()
            else:
                raise ValueError(f"Memory {record.memory_id} not found.")

    def delete(self, memory_id: str) -> bool:
        with self._lock:
            if memory_id in self._memories:
                del self._memories[memory_id]
                self._save()
                return True
            return False

    def get_all(self) -> List[MemoryRecord]:
        with self._lock:
            # Deterministic ordering by created_at descending
            records = list(self._memories.values())
            records.sort(key=lambda r: r.created_at, reverse=True)
            return records

    def statistics(self) -> MemoryStatistics:
        with self._lock:
            by_type = {t.value: 0 for t in MemoryType}
            by_importance = {i.value: 0 for i in MemoryImportance}
            tags_set = set()
            
            for record in self._memories.values():
                by_type[record.type.value] = by_type.get(record.type.value, 0) + 1
                by_importance[record.importance.value] = by_importance.get(record.importance.value, 0) + 1
                for tag in record.tags:
                    tags_set.add(tag)
                    
            try:
                size = os.path.getsize(self._file_path)
            except OSError:
                size = 0
                
            return MemoryStatistics(
                total_memories=len(self._memories),
                by_type=by_type,
                by_importance=by_importance,
                total_tags=len(tags_set),
                storage_size_bytes=size
            )
