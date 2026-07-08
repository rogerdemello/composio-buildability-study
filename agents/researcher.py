"""Researcher agent: app in -> one AppResult out, with per-field provenance.

Flow:  gather evidence (providers) -> Claude extracts each field w/ confidence+source
       -> build Field objects tagged by which provider surfaced the URL -> score.
"""

from __future__ import annotations

import asyncio

from llm import LLM
from models.app import AppResult, Evidence, Field, score_buildability
from prompts import RESEARCH_SYSTEM, RESEARCH_USER, EXTRACT_INSTRUCTION

# per-field object: value + confidence + evidence_url
_F = lambda desc, value_schema: {  # noqa: E731
    "type": "object", "additionalProperties": False,
    "required": ["value", "confidence", "evidence_url"],
    "properties": {
        "value": value_schema,
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence_url": {"type": "string"},
    },
    "description": desc,
}

EMIT_RECORD = {
    "name": "emit_record",
    "description": "Emit the structured research record; every field carries value+confidence+evidence_url.",
    "input_schema": {
        "type": "object", "additionalProperties": False,
        "required": ["one_liner", "auth_methods", "access", "api_surface", "api_breadth",
                     "has_mcp", "composio_toolkit", "buildability", "main_blocker", "needs_browser"],
        "properties": {
            "one_liner": _F("<=12 words", {"type": "string"}),
            "auth_methods": _F("auth methods", {"type": "array", "items": {"type": "string"}}),
            "access": _F("access model", {"type": "string"}),
            "api_surface": _F("REST/GraphQL/etc", {"type": "string"}),
            "api_breadth": _F("broad/moderate/narrow", {"type": "string"}),
            "has_mcp": _F("official/community/none/unknown", {"type": "string"}),
            "composio_toolkit": _F("yes/no/unknown", {"type": "string"}),
            "buildability": _F("easy/moderate/blocked", {"type": "string"}),
            "main_blocker": _F("short, or 'none'", {"type": "string"}),
            "needs_browser": {"type": "boolean",
                              "description": "true if docs were JS-walled/insufficient and a browser pass is warranted"},
        },
    },
}


class ResearchAgent:
    def __init__(self, providers, model=None, provider=None, llm=None):
        import config
        self.providers = providers            # search + fetch providers, in preference order
        self.model = model or config.RESEARCH_MODEL
        self.llm = llm or LLM(self.model, provider)

    async def _gather(self, app: dict, k: int = 4) -> list:
        """Run the search providers concurrently; return deduped candidate docs."""
        queries = [
            f"{app['name']} API documentation authentication",
            f"{app['name']} developer API REST GraphQL",
            f"{app['name']} MCP server model context protocol",
        ]
        tasks = []
        for p in self.providers:
            if hasattr(p, "search"):
                for q in queries[:2]:
                    tasks.append(p.search(q, k=k))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        docs, seen = [], set()
        for r in results:
            if isinstance(r, Exception):
                continue
            for d in r:
                if d.url and d.url not in seen and d.text:
                    seen.add(d.url)
                    docs.append(d)
        return docs[:8]

    def _context(self, docs) -> str:
        return "\n\n".join(f"[{d.retrieved_by}] {d.url}\n{d.text[:2500]}" for d in docs) or "(no docs retrieved)"

    async def research(self, app: dict) -> AppResult:
        docs = await self._gather(app)
        # map url -> which provider surfaced it, for provenance
        provider_of = {d.url: d.retrieved_by for d in docs}

        rec = await self.llm.structured(
            system=RESEARCH_SYSTEM,
            user=RESEARCH_USER.format(name=app["name"], category=app["category"],
                                      hint=app.get("hint", ""), context=self._context(docs))
                 + "\n\n" + EXTRACT_INSTRUCTION,
            tool_name="emit_record", tool_desc=EMIT_RECORD["description"],
            schema=EMIT_RECORD["input_schema"], max_tokens=2000,
        )

        result = AppResult(id=app["id"], name=app["name"], category=app["category"])
        for key in ["one_liner", "auth_methods", "access", "api_surface", "api_breadth",
                    "has_mcp", "composio_toolkit", "buildability", "main_blocker"]:
            cell = rec.get(key, {})
            url = cell.get("evidence_url", "")
            result.fields[key] = Field(
                value=cell.get("value"),
                confidence=float(cell.get("confidence", 0.5)),
                sources=[Evidence(url=url, retrieved_by=provider_of.get(url, "docs_fetcher"))] if url else [],
            )
        result.buildability_score, result.score_breakdown = score_buildability(result)
        result._needs_browser = bool(rec.get("needs_browser"))  # read by the orchestrator's fallback gate
        return result
