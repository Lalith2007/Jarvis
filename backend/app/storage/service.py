from pathlib import Path

from app.config.settings import settings
from app.storage.models import StorageObject


class StorageService:
    def __init__(self):
        self.root = Path(settings.OBSIDIAN_VAULT)

    def save(
        self,
        obj: StorageObject,
    ) -> Path:
        folder = self.root / obj.folder
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / obj.filename

        path.write_text(
            obj.content,
            encoding="utf-8",
        )

        return path

    def read(
        self,
        relative_path: str,
    ) -> str:
        path = self.root / relative_path

        return path.read_text(
            encoding="utf-8",
        )

    def append(
        self,
        relative_path: str,
        content: str,
    ) -> Path:
        path = self.root / relative_path

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(path, "a", encoding="utf-8") as file:
            file.write(content)

        return path


storage = StorageService()
