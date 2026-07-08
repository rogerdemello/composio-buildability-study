"""Tavily search provider — fast, LLM-oriented web search for finding docs."""

from __future__ import annotations

import os

import httpx

from .base import Doc, SearchProvider


class TavilyProvider(SearchProvider):
    name = "tavily"
    ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")

    async def search(self, query: str, k: int = 5) -> list[Doc]:
        if not self.api_key:
            return []
        payload = {
            "api_key": self.api_key, "query": query, "max_results": k,
            "search_depth": "advanced", "include_raw_content": True,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.ENDPOINT, json=payload)
            r.raise_for_status()
            data = r.json()
        return [
            Doc(url=x.get("url", ""),
                text=(x.get("raw_content") or x.get("content") or "")[:20000],
                title=x.get("title", ""), retrieved_by=self.name)
            for x in data.get("results", [])
        ]
