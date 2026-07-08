"""Firecrawl provider — clean markdown extraction of docs pages (search + scrape)."""

from __future__ import annotations

import os

import httpx

from .base import Doc, FetchProvider, SearchProvider


class FirecrawlProvider(SearchProvider, FetchProvider):
    name = "firecrawl"
    BASE = "https://api.firecrawl.dev/v1"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def search(self, query: str, k: int = 5) -> list[Doc]:
        if not self.api_key:
            return []
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(f"{self.BASE}/search",
                                  headers=self._headers(),
                                  json={"query": query, "limit": k,
                                        "scrapeOptions": {"formats": ["markdown"]}})
            r.raise_for_status()
            data = r.json()
        out = []
        for x in data.get("data", []):
            out.append(Doc(url=x.get("url", ""),
                           text=(x.get("markdown") or x.get("description") or "")[:20000],
                           title=x.get("title", ""), retrieved_by=self.name))
        return out

    async def fetch(self, url: str) -> Doc | None:
        if not self.api_key:
            return None
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(f"{self.BASE}/scrape",
                                  headers=self._headers(),
                                  json={"url": url, "formats": ["markdown"]})
            if r.status_code >= 400:
                return None
            data = r.json().get("data", {})
        return Doc(url=url, text=(data.get("markdown") or "")[:20000],
                   title=data.get("metadata", {}).get("title", ""), retrieved_by=self.name)
