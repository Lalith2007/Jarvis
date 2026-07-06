import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    SUMMARY = "summary"


class MemoryImportance(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryVisibility(str, Enum):
    PRIVATE = "private"
    INTERNAL = "internal"
    PUBLIC = "public"


class MemoryRecord(BaseModel):
    memory_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default_user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: MemoryType = MemoryType.FACT
    importance: MemoryImportance = MemoryImportance.NORMAL
    visibility: MemoryVisibility = MemoryVisibility.INTERNAL
    source: str = "system"
    tags: List[str] = Field(default_factory=list)
    title: str = ""
    summary: str = ""
    content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        return cls.model_validate(data)

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> "MemoryRecord":
        return cls.model_validate_json(json_str)


class MemoryQuery(BaseModel):
    query: str
    types: Optional[List[MemoryType]] = None
    min_importance: Optional[MemoryImportance] = None
    tags: Optional[List[str]] = None
    limit: int = 5
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryQuery":
        return cls.model_validate(data)


class MemoryCandidate(BaseModel):
    record: MemoryRecord
    score: float
    matched_tags: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)


class MemorySearchResult(BaseModel):
    query: MemoryQuery
    results: List[MemoryRecord]
    total_candidates_evaluated: int
    execution_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class MemoryWriteResult(BaseModel):
    memory_id: str
    status: str
    action: str  # created, updated
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class MemoryReadResult(BaseModel):
    memory_id: str
    record: Optional[MemoryRecord]
    found: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class MemoryStatistics(BaseModel):
    total_memories: int
    by_type: Dict[str, int]
    by_importance: Dict[str, int]
    total_tags: int
    storage_size_bytes: int
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
