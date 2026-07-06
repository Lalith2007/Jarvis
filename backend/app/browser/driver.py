"""
Browser driver abstraction (Sprint 13.6).

`BrowserDriver` is the interface browser capabilities call; `PlaywrightDriver`
is the real implementation (lazy-imported so the backend runs without browser
binaries installed). `browser_manager` holds the active driver and is
driver-injectable for hermetic tests (FakeBrowserDriver).

Sessions map to isolated Playwright browser contexts, giving per-session cookie
persistence and multi-tab isolation.
"""

from abc import ABC, abstractmethod
from typing import Any


class BrowserDriver(ABC):
    @abstractmethod
    def navigate(self, session_id: str, url: str) -> dict: ...

    @abstractmethod
    def extract(self, session_id: str, selector: str | None = None) -> str: ...

    @abstractmethod
    def click(self, session_id: str, selector: str) -> None: ...

    @abstractmethod
    def fill(self, session_id: str, selector: str, value: str) -> None: ...

    @abstractmethod
    def capture(self, session_id: str, kind: str, path: str) -> str: ...

    @abstractmethod
    def cookies(self, session_id: str) -> list[dict]: ...

    def available(self) -> bool:
        return True

    def close(self, session_id: str) -> None:  # pragma: no cover - optional
        pass


class PlaywrightDriver(BrowserDriver):
    """Real driver. Requires `playwright install` for browser binaries."""

    def __init__(self):
        self._pw = None
        self._browser = None
        self._contexts: dict[str, Any] = {}
        self._pages: dict[str, Any] = {}

    def available(self) -> bool:
        try:
            import playwright  # noqa: F401
            return True
        except Exception:
            return False

    def _page(self, session_id: str):
        if self._pw is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=True)
        if session_id not in self._pages:
            ctx = self._browser.new_context()
            self._contexts[session_id] = ctx
            self._pages[session_id] = ctx.new_page()
        return self._pages[session_id]

    def navigate(self, session_id, url):
        page = self._page(session_id)
        page.goto(url)
        return {"url": page.url, "title": page.title()}

    def extract(self, session_id, selector=None):
        page = self._page(session_id)
        if selector:
            el = page.query_selector(selector)
            return el.inner_text() if el else ""
        return page.inner_text("body")

    def click(self, session_id, selector):
        self._page(session_id).click(selector)

    def fill(self, session_id, selector, value):
        self._page(session_id).fill(selector, value)

    def capture(self, session_id, kind, path):
        page = self._page(session_id)
        if kind == "pdf":
            page.pdf(path=path)
        else:
            page.screenshot(path=path, full_page=True)
        return path

    def cookies(self, session_id):
        ctx = self._contexts.get(session_id)
        return ctx.cookies() if ctx else []

    def close(self, session_id):
        page = self._pages.pop(session_id, None)
        ctx = self._contexts.pop(session_id, None)
        if page:
            page.close()
        if ctx:
            ctx.close()


class BrowserManager:
    def __init__(self):
        self._driver: BrowserDriver | None = None

    def set_driver(self, driver: BrowserDriver) -> None:
        self._driver = driver

    def driver(self) -> BrowserDriver:
        if self._driver is None:
            self._driver = PlaywrightDriver()
        return self._driver


browser_manager = BrowserManager()
