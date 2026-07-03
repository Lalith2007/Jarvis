from pathlib import Path

from pydantic import BaseModel


class Document(BaseModel):
    folder: str

    filename: str

    content: str

    path: Path | None = None
