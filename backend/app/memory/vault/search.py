from app.memory.vault.indexer import vault_index
from app.memory.vault.models import SearchResult
from app.query.models import ProcessedQuery


class VaultSearch:
    """
    Keyword-based vault search.

    Supports both:

        vault_search.search("ISRO")

    and

        vault_search.search(processed_query)
    """

    def _normalize_query(
        self,
        query: str | ProcessedQuery,
    ) -> list[str]:

        if isinstance(query, ProcessedQuery):
            return [
                keyword.lower()
                for keyword in query.keywords
            ]

        return [
            keyword.lower()
            for keyword in str(query).split()
        ]

    def search(
        self,
        query: str | ProcessedQuery,
    ) -> list[SearchResult]:

        keywords = self._normalize_query(query)

        results: list[SearchResult] = []

        for note in vault_index.all_notes():

            score = 0
            matched: list[str] = []

            title = note.title.lower()
            path = note.path.lower()
            content = note.content.lower()

            for keyword in keywords:

                if keyword == title:
                    score += 100
                    matched.append("exact_title")

                elif keyword in title:
                    score += 60
                    matched.append("title")

                if keyword in path:
                    score += 30
                    matched.append("path")

                if keyword in content:
                    score += 10
                    matched.append("content")

            if score > 0:
                results.append(
                    SearchResult(
                        score=score,
                        matched_fields=matched,
                        note=note,
                    )
                )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results


vault_search = VaultSearch()
