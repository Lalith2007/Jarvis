import re

from app.query.models import ProcessedQuery
from app.query.stopwords import STOPWORDS


class QueryProcessor:
    def process(
        self,
        text: str,
    ) -> ProcessedQuery:

        original = text

        normalized = text.lower()

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        keywords = [
            word
            for word in normalized.split()
            if word not in STOPWORDS
        ]

        normalized = " ".join(keywords)

        return ProcessedQuery(
            original=original,
            normalized=normalized,
            keywords=keywords,
        )


query_processor = QueryProcessor()
