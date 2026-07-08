"""
live_demo.py — a genuine, grounded live run of the research agent on the 5 golden apps.

Uses the real providers (Tavily + Firecrawl for retrieval) and NVIDIA NIM for extraction,
and writes to output/live_run_golden.json. It deliberately does NOT touch the verified
100-app dataset (output/results.json) — this is a proof-of-liveness artifact.

    python -m scripts.live_demo            # 5 golden apps
    python -m scripts.live_demo --ids 81   # a single app (e.g. Stripe)
"""

from __future__ import annotations

import argparse
import asyncio
import json

import config
from agents.researcher import ResearchAgent
from providers.tavily import TavilyProvider
from providers.firecrawl import FirecrawlProvider
from providers.docs_fetcher import DocsFetcher
from providers.composio_search import ComposioSearchProvider


async def run(ids=None):
    apps = json.loads((config.DATA / "apps_input.json").read_text(encoding="utf-8"))
    if ids:
        apps = [a for a in apps if a["id"] in ids]
    else:
        apps = [a for a in apps if a["name"] in config.GOLDEN]

    providers = [ComposioSearchProvider(), TavilyProvider(), FirecrawlProvider(), DocsFetcher()]
    researcher = ResearchAgent(providers, model=config.RESEARCH_MODEL)
    out = []
    for app in apps:
        print(f"[research] {app['name']} (model={config.RESEARCH_MODEL})", flush=True)
        res = await researcher.research(app)
        auth = res.val("auth_methods")
        src = res.fields["auth_methods"].sources
        print(f"   auth={auth} access={res.val('access')} api={res.val('api_surface')} "
              f"mcp={res.val('has_mcp')} score={res.buildability_score}")
        print(f"   evidence={src[0].url if src else '(none)'}  via={src[0].retrieved_by if src else '-'}")
        out.append(res.to_dict())
        # write incrementally so a slow/timed-out run still persists what completed
        (config.OUTPUT / "live_run_golden.json").write_text(
            json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {len(out)} live-researched apps -> output/live_run_golden.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    a = ap.parse_args()
    ids = {int(x) for x in a.ids.split(",")} if a.ids else None
    asyncio.run(run(ids))
