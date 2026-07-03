from app.memory.vault.reader import vault_reader
from app.memory.vault.models import VaultNote


class VaultIndexer:
    def __init__(self):
        self.notes: list[VaultNote] = []

    def build(self):
        self.notes = vault_reader.read_notes()

    def all_notes(self) -> list[VaultNote]:
        return self.notes


vault_index = VaultIndexer()
