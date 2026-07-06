import os
import tempfile
from app.memory.storage.local import LocalMemoryStorage
from app.memory.core.models import MemoryRecord, MemoryType

def test_local_storage_crud():
    with tempfile.TemporaryDirectory() as temp_dir:
        store_path = os.path.join(temp_dir, "memory.json")
        storage = LocalMemoryStorage(file_path=store_path)
        
        # 1. Create
        record1 = MemoryRecord(title="First", content="A")
        storage.store(record1)
        
        assert len(storage.get_all()) == 1
        
        # 2. Retrieve
        retrieved = storage.retrieve(record1.memory_id)
        assert retrieved is not None
        assert retrieved.title == "First"
        
        # 3. Update
        record1.content = "B"
        storage.update(record1)
        retrieved_updated = storage.retrieve(record1.memory_id)
        assert retrieved_updated.content == "B"
        
        # 4. Delete
        assert storage.delete(record1.memory_id) is True
        assert storage.retrieve(record1.memory_id) is None
        assert len(storage.get_all()) == 0

def test_local_storage_recovery():
    with tempfile.TemporaryDirectory() as temp_dir:
        store_path = os.path.join(temp_dir, "memory.json")
        
        # Corrupt file
        with open(store_path, "w") as f:
            f.write("corrupted JSON {")
            
        # Storage should recover gracefully (start empty)
        storage = LocalMemoryStorage(file_path=store_path)
        assert len(storage.get_all()) == 0
        
        # Storage should be able to save new records
        storage.store(MemoryRecord(title="New"))
        assert len(storage.get_all()) == 1
