from pathlib import Path

from app.config.settings import settings
from app.documents.models import Document


class DocumentService:
    def _root(self) -> Path:
        if not settings.VAULT_PATH:
            raise RuntimeError(
                "No vault configured — set OBSIDIAN_VAULT/VAULT_PATH to write documents."
            )
        return Path(settings.VAULT_PATH)

    def write(self, document: Document) -> Path:
        folder = self._root() / document.folder
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / document.filename

        path.write_text(
            document.content,
            encoding="utf-8",
        )

        return path


document_service = DocumentService()
