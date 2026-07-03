from pathlib import Path

from app.config.settings import settings
from app.memory.vault.models import VaultNote


class VaultReader:
    def __init__(self):
        self.root = Path(settings.OBSIDIAN_VAULT)

    def read_notes(self) -> list[VaultNote]:
        notes = []

        for file in self.root.rglob("*.md"):
            parts = file.parts

            if any(part.startswith(".") for part in parts):
                continue

            try:
                notes.append(
                    VaultNote(
                        path=str(file.relative_to(self.root)),
                        title=file.stem,
                        content=file.read_text(encoding="utf-8"),
                    )
                )
            except Exception:
                continue

        return notes


vault_reader = VaultReader()
