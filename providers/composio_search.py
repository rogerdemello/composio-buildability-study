"""Composio's own search tools as a provider.

Dogfooding: the same COMPOSIO_SEARCH toolkit Composio ships to customers is used
to power the researcher. Uses the Composio SDK if available; otherwise no-ops so
the pipeline still runs on the other providers.
"""

from __future__ import annotations

import asyncio
import os

from .base import Doc, SearchProvider


class ComposioSearchProvider(SearchProvider):
    name = "composio_search"

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id or os.environ.get("COMPOSIO_USER_ID", "default")
        self._composio = None
        self._tools = None

    def _ensure(self) -> bool:
        if self._composio is not None:
            return True
        if not os.environ.get("COMPOSIO_API_KEY"):
            return False
        try:
            from composio import Composio
            self._composio = Composio()
            # COMPOSIO_SEARCH exposes web/news search actions
            self._tools = self._composio.tools.get(user_id=self.user_id, toolkits=["COMPOSIO_SEARCH"])
            return True
        except Exception:
            return False

    async def search(self, query: str, k: int = 5) -> list[Doc]:
        if not self._ensure():
            return []

        def _call():
            # Execute the search action directly through the SDK.
            res = self._composio.tools.execute(
                "COMPOSIO_SEARCH_SEARCH",
                user_id=self.user_id,
                arguments={"query": query},
            )
            items = (res or {}).get("data", {}).get("results", []) if isinstance(res, dict) else []
            return items[:k]

        try:
            items = await asyncio.to_thread(_call)
        except Exception:
            return []
        return [Doc(url=x.get("url", ""), text=(x.get("content") or "")[:20000],
                    title=x.get("title", ""), retrieved_by=self.name) for x in items]
