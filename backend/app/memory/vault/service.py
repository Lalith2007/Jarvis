from app.memory.vault.indexer import vault_index
from app.memory.vault.search import vault_search
from app.memory.vault.models import VaultNote, SearchResult
from app.query.models import ProcessedQuery

class VaultService:
    def __init__(self):
        self._ready = False

    def build(self):
        if not self._ready:
            vault_index.build()
            self._ready = True

    def notes(self) -> list[VaultNote]:
        self.build()
        return vault_index.all_notes()
    def search(
      self,
      query: ProcessedQuery,
      limit: int = 5,
    ) -> list[SearchResult]:

       self.build()

       return vault_search.search(query)[:limit]

    def read(self, path: str) -> VaultNote | None:
        self.build()

        for note in vault_index.all_notes():
            if note.path == path:
                return note

        return None


vault = VaultService()
