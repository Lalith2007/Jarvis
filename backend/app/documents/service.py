from pathlib import Path

from app.config.settings import settings
from app.documents.models import Document


class DocumentService:
    def __init__(self):
        self.root = Path(settings.VAULT_PATH)

    def write(self, document: Document) -> Path:
        folder = self.root / document.folder
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / document.filename

        path.write_text(
            document.content,
            encoding="utf-8",
        )

        return path


document_service = DocumentService()
