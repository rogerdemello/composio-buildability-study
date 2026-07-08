"""Playwright browser provider — the *fallback*, not the default.

Only invoked when cheaper providers fail: JS-rendered docs, login walls that
still show pricing/auth above the fold, or when the verifier flags an
inconsistency it wants a rendered page to settle. See main.py for the gate.
"""

from __future__ import annotations

from .base import Doc, FetchProvider


class BrowserProvider(FetchProvider):
    name = "browser"

    def __init__(self):
        self._pw = None
        self._browser = None

    async def _ensure(self):
        if self._browser is None:
            from playwright.async_api import async_playwright  # lazy: heavy import
            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(headless=True)

    async def fetch(self, url: str) -> Doc | None:
        try:
            await self._ensure()
            page = await self._browser.new_page(user_agent="Mozilla/5.0 composio-research")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            text = await page.inner_text("body")
            title = await page.title()
            await page.close()
            return Doc(url=url, text=text[:20000], title=title, retrieved_by=self.name)
        except Exception:
            return None

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()
