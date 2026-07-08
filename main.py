"""
Orchestrator. Async, rate-limited, resumable, with a browser fallback gate.

    python main.py research               # research all 100 (async, Semaphore(5))
    python main.py research --golden      # just the 5 golden apps (pipeline dev loop)
    python main.py research --ids 1,4,55
    python main.py verify --sample 20     # independent audit of a stratified sample
    python main.py patterns               # LLM pattern engine over the dataset
    python main.py report                 # render the case study from JSON
    python main.py all                    # research -> verify -> patterns -> report
"""

from __future__ import annotations

import argparse
import asyncio
import json

import config
from agents import MarkdownWriter, PatternAnalyzer, ReportWriter, ResearchAgent, VerifyAgent
from database.store import Store


def load_apps() -> list[dict]:
    return json.loads((config.DATA / "apps_input.json").read_text(encoding="utf-8"))


def make_providers():
    """Preference order: Composio search -> Tavily -> Firecrawl -> plain fetch.
    Browser is constructed lazily and only used by the fallback gate."""
    from providers.composio_search import ComposioSearchProvider
    from providers.tavily import TavilyProvider
    from providers.firecrawl import FirecrawlProvider
    from providers.docs_fetcher import DocsFetcher
    return [ComposioSearchProvider(), TavilyProvider(), FirecrawlProvider(), DocsFetcher()]


async def _research(ids=None, golden=False):
    apps = load_apps()
    if golden:
        apps = [a for a in apps if a["name"] in config.GOLDEN]
    if ids:
        apps = [a for a in apps if a["id"] in ids]

    providers = make_providers()
    researcher = ResearchAgent(providers, model=config.RESEARCH_MODEL)
    store = Store(config.OUTPUT / "results.json")
    store.run.meta.providers = [p.name for p in providers]

    sem = asyncio.Semaphore(config.CONCURRENCY)     # <-- rate limiting

    async def one(app):
        if store.has(app["id"]):
            return
        async with sem:
            try:
                res = await researcher.research(app)
                # browser fallback ONLY when the researcher flagged insufficient docs
                if getattr(res, "_needs_browser", False):
                    from providers.browser import BrowserProvider
                    br = BrowserProvider()
                    doc = await br.fetch(app.get("hint_url") or f"https://{app['hint'].split()[0]}")
                    await br.close()
                    if doc:
                        res = await researcher.research({**app, "hint": app["hint"] + " " + doc.text[:1500]})
                store.upsert(res)
                store.save()
                print(f"  ✓ {app['name']}  score={res.buildability_score}  conf={res.app_confidence()}")
            except Exception as e:
                print(f"  ✗ {app['name']}: {e}")

    await asyncio.gather(*(one(a) for a in apps))
    store.save()
    print(f"research done -> {store.path}  ({len(store.run.apps)} apps)")


async def _verify(sample):
    from agents.verifier import GRADED  # noqa
    store = Store(config.OUTPUT / "results.json")
    providers = make_providers()
    researcher = ResearchAgent(providers, model=config.RESEARCH_MODEL)
    verifier = VerifyAgent(researcher, model=config.VERIFY_MODEL)
    apps_meta = {a["id"]: a for a in load_apps()}

    # stratified sample across categories
    by_cat: dict[str, list] = {}
    for a in store.run.apps:
        by_cat.setdefault(a.category, []).append(a)
    picks, i, cats = [], 0, sorted(by_cat)
    while len(picks) < sample and any(by_cat.values()):
        c = cats[i % len(cats)]
        if by_cat[c]:
            picks.append(by_cat[c].pop(0))
        i += 1

    sem = asyncio.Semaphore(config.CONCURRENCY)
    async def one(a):
        async with sem:
            await verifier.verify(apps_meta[a.id], a)
            store.upsert(a)
            print(f"  audited {a.name}")
    await asyncio.gather(*(one(a) for a in picks))
    store.save()
    print(f"verify done on {len(picks)} apps -> {store.path}")


async def _patterns():
    store = Store(config.OUTPUT / "results.json")
    patterns = await PatternAnalyzer(model=config.PATTERN_MODEL).analyze(store.run)
    (config.OUTPUT / "patterns.json").write_text(json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8")
    print("patterns:", patterns.get("headline"))


def _report():
    ReportWriter().build()
    print("report -> web/index.html")


def _md():
    MarkdownWriter().build()
    print("markdown -> CASE_STUDY.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["research", "verify", "patterns", "report", "md", "all"])
    ap.add_argument("--ids"); ap.add_argument("--golden", action="store_true")
    ap.add_argument("--sample", type=int, default=config.VERIFY_SAMPLE)
    a = ap.parse_args()
    ids = {int(x) for x in a.ids.split(",")} if a.ids else None

    if a.cmd == "research":
        asyncio.run(_research(ids, a.golden))
    elif a.cmd == "verify":
        asyncio.run(_verify(a.sample))
    elif a.cmd == "patterns":
        asyncio.run(_patterns())
    elif a.cmd == "report":
        _report()
    elif a.cmd == "md":
        _md()
    elif a.cmd == "all":
        asyncio.run(_research(ids, a.golden))
        asyncio.run(_verify(a.sample))
        asyncio.run(_patterns())
        _report()
        _md()


if __name__ == "__main__":
    main()
