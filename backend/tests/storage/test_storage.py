from app.storage.models import StorageObject
from app.storage.service import storage


def test_storage_save_and_read():
    obj = StorageObject(
        folder="jarvis/test",
        filename="hello.md",
        content="# Hello\n\nThis is a storage test.",
    )

    path = storage.save(obj)

    assert path.exists()

    content = storage.read("jarvis/test/hello.md")

    assert "Hello" in content
    assert "storage test" in content
