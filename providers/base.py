"""Provider interface: a uniform async surface over search + fetch backends.

Every provider returns Doc objects tagged with `retrieved_by`, so a field's
provenance always knows which tool actually pulled the evidence.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class Doc:
    url: str
    text: str
    retrieved_by: str
    title: str = ""


class SearchProvider(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    async def search(self, query: str, k: int = 5) -> list[Doc]:
        """Return up to k candidate docs for a query."""


class FetchProvider(abc.ABC):
    name: str = "base"

    @abc.abstractmethod
    async def fetch(self, url: str) -> Doc | None:
        """Fetch and return the readable content of a single URL."""
