from pathlib import Path

from app.config.settings import settings


class MemoryService:
    def __init__(self):
        self.vault = Path(settings.OBSIDIAN_VAULT)

    def read(self, relative_path: str) -> str:
        file_path = self.vault / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"{relative_path} not found.")

        return file_path.read_text(encoding="utf-8")


memory = MemoryService()
