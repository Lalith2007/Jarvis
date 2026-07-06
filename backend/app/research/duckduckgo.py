"""
Keyless DuckDuckGo search provider (Sprint 13.7 live binding).

Uses the DDG HTML endpoint — no API key — so grounded research works out of the
box. Bind via research_manager.set_provider(DuckDuckGoProvider()).
"""
import re
import html as _html

import httpx

from app.research.provider import SearchProvider, SearchHit


class DuckDuckGoProvider(SearchProvider):
    _URL = "https://html.duckduckgo.com/html/"

    def available(self) -> bool:
        return True

    def search(self, query: str, limit: int = 8) -> list[SearchHit]:
        try:
            r = httpx.post(self._URL, data={"q": query}, timeout=15.0,
                           headers={"User-Agent": "Mozilla/5.0 JARVIS"})
            body = r.text
        except Exception:
            return []
        hits: list[SearchHit] = []
        # result links: <a class="result__a" href="...">Title</a>
        for m in re.finditer(r'result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', body, re.S):
            url = _html.unescape(m.group(1))
            title = _html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
            if url and title:
                hits.append(SearchHit(title=title, url=url, snippet="", source_type="web"))
            if len(hits) >= limit:
                break
        return hits

    def fetch(self, url: str) -> str:
        try:
            r = httpx.get(url, timeout=15.0, headers={"User-Agent": "Mozilla/5.0 JARVIS"}, follow_redirects=True)
            text = re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)
            return re.sub(r"<[^>]+>", " ", text)[:6000]
        except Exception:
            return ""
