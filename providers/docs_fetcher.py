"""Plain HTTP docs fetcher — the zero-dependency fallback (also used for evidence
liveness checks). Strips tags to rough text. No API key required."""

from __future__ import annotations

import re

import httpx

from .base import Doc, FetchProvider

_TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
_ANGLE = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _to_text(html: str) -> str:
    html = _TAG.sub(" ", html)
    return _WS.sub(" ", _ANGLE.sub(" ", html)).strip()


class DocsFetcher(FetchProvider):
    name = "docs_fetcher"

    async def fetch(self, url: str) -> Doc | None:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; composio-research/1.0)"}
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
                r = await client.get(url)
                if r.status_code >= 400:
                    return None
                return Doc(url=str(r.url), text=_to_text(r.text)[:20000], retrieved_by=self.name)
        except Exception:
            return None

    async def is_live(self, url: str) -> tuple[bool, int | str]:
        """Liveness probe used by the verifier's evidence check."""
        headers = {"User-Agent": "Mozilla/5.0 (compatible; composio-research/1.0)"}
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=headers) as client:
                r = await client.get(url)
                # 401/403/429 mean the endpoint exists but gates the bot -> still "live"
                return (r.status_code < 400 or r.status_code in (401, 403, 429), r.status_code)
        except Exception as e:
            return (False, str(e)[:40])
