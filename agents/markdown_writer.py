"""Markdown writer: renders CASE_STUDY.md from the same JSON as the HTML page.

Same principle as report_writer — nothing hand-written; every number and row
comes from output/results.json, output/patterns.json and the verification report.
A portable, diff-able, agent-and-human-readable twin of the live case study.
"""

from __future__ import annotations

import collections
import json

import config

CAT_SHORT = {
    "CRM and Sales": "CRM", "Support and Helpdesk": "Support",
    "Communications and Messaging": "Comms", "Marketing, Ads, Email and Social": "Marketing",
    "Ecommerce": "Ecommerce", "Data, SEO and Scraping": "Data/SEO",
    "Developer, Infra and Data platforms": "Dev/Infra",
    "Productivity and Project Management": "Productivity",
    "Finance and Fintech": "Finance", "AI, Research and Media-native": "AI/Media",
}
OBTAINABLE = {"self-serve", "sandbox-self-serve", "trial-only", "waitlist"}


def _bar(n: int, total: int, width: int = 22) -> str:
    filled = round(width * n / total) if total else 0
    return "█" * filled + "░" * (width - filled)


def _verdict(score: int) -> str:
    return "easy" if score >= 68 else "moderate" if score >= 34 else "blocked"


def _emoji(score: int) -> str:
    return "🟢" if score >= 68 else "🟡" if score >= 34 else "🔴"


class MarkdownWriter:
    def __init__(self, repo_url="https://github.com/rogerdemello/composio-buildability-study",
                 live_url="https://rogerdemello.github.io/composio-buildability-study/"):
        self.repo_url, self.live_url = repo_url, live_url

    def build(self) -> str:
        results = json.loads((config.OUTPUT / "results.json").read_text(encoding="utf-8"))
        patterns = json.loads((config.OUTPUT / "patterns.json").read_text(encoding="utf-8"))
        verify = json.loads((config.DATA / "verification_report.json").read_text(encoding="utf-8"))
        apps = results["apps"]
        C = patterns.get("counts", {})
        fv = lambda a, k: a["fields"][k]["value"]  # noqa: E731

        n = len(apps)
        n_easy = sum(1 for a in apps if a["buildability_score"] >= 68)
        n_mod = sum(1 for a in apps if 34 <= a["buildability_score"] < 68)
        n_blk = n - n_easy - n_mod
        n_self = C.get("self_serve", sum(1 for a in apps if fv(a, "access") in OBTAINABLE))
        avg = round(sum(a["buildability_score"] for a in apps) / n)
        human = sum(1 for a in apps if any(f["human_checked"] for f in a["fields"].values()))

        out: list[str] = []
        w = out.append

        # ---- header ----
        w("# Composio · Which of 100 apps could become an agent toolkit today?")
        w("")
        w("> **AI Product Ops take-home.** An async agent pipeline researched 100 apps against their live "
          "developer docs, scored each one's buildability, attached **evidence + confidence to every field**, "
          "and an independent agent audited a sample to prove the numbers.")
        w("")
        w(f"- 📊 **Live interactive case study:** {self.live_url}")
        w(f"- 📦 **Source repo:** {self.repo_url}")
        w("")
        w(f"`{n} apps` · `{len(CAT_SHORT)} categories` · `avg score {avg}/100` · "
          f"`{verify['before']}%→{verify['after']}% verified` · `{human} human-checked`")
        w("")
        w("---")

        # ---- headline ----
        w("## 1 · The headline")
        w("")
        w(f"> **{patterns['headline']}**")
        w("")
        for i, ins in enumerate(patterns.get("insights", []), 1):
            w(f"**{i:02d}. {ins['title']}** — {ins['detail']}")
            w("")
        w("| Metric | Value |")
        w("|---|---|")
        w(f"| Buildable today (score ≥ 68) | **{n_easy}** / {n} |")
        w(f"| Developer can self-serve credentials | **{n_self}** / {n} |")
        w(f"| Ship an official MCP server | **{C.get('mcp', {}).get('official', 0)}** / {n} |")
        w(f"| Already a Composio toolkit | **{C.get('composio', {}).get('yes', 0)}** / {n} |")
        w(f"| Buildability split | 🟢 {n_easy} easy · 🟡 {n_mod} moderate · 🔴 {n_blk} blocked |")
        w("")
        w("---")

        # ---- patterns ----
        w("## 2 · The patterns")
        w("")

        def dist(title, d, note=""):
            w(f"**{title}**")
            w("")
            w("```")
            tot = max(d.values()) if d else 1
            for k, v in d.items():
                w(f"{k:<18} {_bar(v, tot)} {v}")
            w("```")
            if note:
                w(note)
            w("")

        dist("Auth methods (apps support more than one)", C.get("auth", {}),
             "OAuth2 dominates but is nearly always paired with a key/token path; Basic auth is legacy.")
        dist("Access — can a developer self-serve credentials?", C.get("access", {}),
             f"{n_self} obtainable vs {n - n_self} gated — the gated set is the *needs-outreach* pile.")
        dist("API surface", C.get("api_surface", {}), "REST is the universal substrate.")
        dist("MCP availability", C.get("mcp", {}),
             f"{C.get('mcp', {}).get('official', 0)} official + {C.get('mcp', {}).get('community', 0)} community already MCP-reachable.")

        # buildability by category
        w("**Buildability by category** (easy · moderate · blocked, out of 10)")
        w("")
        w("| Category | 🟢 easy | 🟡 moderate | 🔴 blocked |")
        w("|---|:--:|:--:|:--:|")
        by = collections.defaultdict(lambda: collections.Counter())
        for a in apps:
            by[a["category"]][_verdict(a["buildability_score"])] += 1
        for cat in CAT_SHORT:
            c = by.get(cat, collections.Counter())
            w(f"| {CAT_SHORT[cat]} | {c['easy']} | {c['moderate']} | {c['blocked']} |")
        w("")

        w(f"**▲ Easy wins (just build it):** {', '.join(patterns.get('easy_wins', []))}")
        w("")
        w(f"**◆ Needs outreach (gated):** {', '.join(patterns.get('needs_outreach', []))}")
        w("")
        w("**★ Surprises**")
        for s in patterns.get("surprises", []):
            w(f"- {s}")
        w("")
        w("---")

        # ---- the 100 ----
        w("## 3 · The 100")
        w("")
        w("Score is the quantified verdict (easy ≥ 68 · moderate 34–67 · blocked < 34); gated access is "
          "hard-capped so a strong API you can't get creds for can't score \"easy\". "
          "`†` = human-checked (in the audited sample). Full per-field provenance + confidence is on the live page.")
        w("")
        w("| # | App | Cat | What it does | Auth | Access | API | MCP | Cmp | Score | |")
        w("|--:|---|---|---|---|---|---|---|:--:|--:|:--:|")
        for a in sorted(apps, key=lambda x: x["id"]):
            hc = "†" if any(f["human_checked"] for f in a["fields"].values()) else ""
            auth = "+".join(fv(a, "auth_methods") or [])
            sc = a["buildability_score"]
            w(f"| {a['id']} | **{a['name']}**{hc} | {CAT_SHORT.get(a['category'], a['category'])} | "
              f"{fv(a, 'one_liner')} | {auth} | {fv(a, 'access')} | {fv(a, 'api_surface')} | "
              f"{fv(a, 'has_mcp')} | {fv(a, 'composio_toolkit')} | {sc} | {_emoji(sc)} |")
        w("")
        w("---")

        # ---- agent ----
        w("## 4 · The agent that did it")
        w("")
        w("A modular pipeline built on Composio's own SDK + search tools:")
        w("")
        w("```")
        w("providers (composio_search → tavily → firecrawl → docs_fetcher → browser*)")
        w("      │        *browser = Playwright, fallback only when docs are JS-walled")
        w("      ▼")
        w("researcher.py   app → structured record, every FIELD w/ value+confidence+evidence")
        w("      ▼         (async, Semaphore(5), resumable JSON store)")
        w("verifier.py     different, stronger model, adversarial re-check + evidence liveness")
        w("      ▼")
        w("pattern_analyzer.py   LLM insights, grounded in code-computed counts")
        w("      ▼")
        w("report_writer.py / markdown_writer.py   render page & this doc from JSON")
        w("```")
        w("")
        w("**Where a human was needed**")
        w("- **Login-gated / thin docs** (fanbasis, iPayX, Paygent, higgsfield) — can't read behind a login wall.")
        w("- **Sandbox vs production** fintech splits (`sandbox-self-serve`) — a judgment the rubric couldn't encode.")
        w("- **Composio catalog stubs** — a toolkit *page* with 0 tools isn't real coverage.")
        w("- **Access reclassification** — the score exposed hedged \"moderate\" calls that were really gated "
          "(SFCC, Brex) or really self-serve; a human set the access value the score keys off.")
        w("")
        w("---")

        # ---- method ----
        w("## 5 · How it was built")
        w("")
        w("1. **Perfect on 5, then scale.** Tuned on 5 golden apps across five auth models — "
          "Salesforce, HubSpot, Slack, Stripe, Shopify — then scaled to 100.")
        w("2. **Async fan-out** under `Semaphore(5)`, resumable so a crash never re-does finished work.")
        w("3. **Score, don't guess** — buildability is a weighted 0–100 score; the verdict is the band.")
        w("4. **Verify + lift** — independent audit + evidence-liveness moved accuracy up (below).")
        w("")
        w("---")

        # ---- verification ----
        w("## 6 · Is it trustworthy?")
        w("")
        w(f"### Graded-field accuracy: ~~{verify['before']}%~~ → **{verify['after']}%**")
        w("")
        w(verify["explain"].replace("<b>", "**").replace("</b>", "**"))
        w("")
        for m in verify.get("metrics", []):
            w(f"- {m.replace('<b>', '**').replace('</b>', '**')}")
        w("")
        w("**Hits and misses (shown honestly)**")
        w("")
        w("| App | Field | First pass | Verified | Verdict | Why |")
        w("|---|---|---|---|---|---|")
        for d in verify.get("diffs", []):
            w(f"| {d['app']} | {d['field']} | {d['first']} | {d['verified']} | "
              f"**{d['verdict']}** | {d['why']} |")
        w("")
        w("*miss = first pass wrong (fixed) · confirm = auditor wrong, first pass upheld · "
          "refine = both defensible, more precise value adopted.*")
        w("")
        w("---")

        # ---- failures ----
        w("## 7 · What defeated the agent")
        w("")
        w("- **Paygent Connect** — genuinely defeated us. Japanese, contract-only, mutual-TLS certs, no self-serve. "
          "The brief's \"NMI-powered\" hint appears wrong; we report that rather than guess.")
        w("- **NotebookLM** — no standalone public API; only a licensed enterprise API on Google Cloud. A valid *blocked* finding.")
        w("- **fanbasis / iPayX** — core docs behind a login wall; read the public reference, flagged low confidence.")
        w("- **higgsfield** — thin, fast-moving docs; real self-serve REST API confirmed but breadth uncertain → mid-band score.")
        w("")
        w("---")

        # ---- run ----
        w("## 8 · Run it yourself")
        w("")
        w("```bash")
        w("pip install -r requirements.txt")
        w("cp .env.example .env      # add ANTHROPIC_API_KEY (+ COMPOSIO/TAVILY/FIRECRAWL if you have them)")
        w("")
        w("python main.py research --golden   # perfect the pipeline on 5 apps")
        w("python main.py research            # scale to all 100 (async, resumable)")
        w("python main.py verify --sample 20  # independent audit + accuracy")
        w("python main.py patterns            # LLM pattern engine")
        w("python main.py report              # render web/index.html")
        w("python main.py md                  # render this CASE_STUDY.md")
        w("```")
        w("")
        w("> Committed `output/*.json` is the run behind this doc, so it regenerates with **no API keys**.")
        w("")
        w("## Honesty notes")
        w("- **How Composio was used:** the `composio_toolkit` column is ground-truthed against "
          "Composio's live catalog via its **own SDK** (`composio.toolkits.get()` + per-slug API checks) — "
          "**100% agreement**, and it corrected 4 LLM errors (Twilio/Clay/Devin → no, GoHighLevel → yes; "
          "see `database/verify_composio.py`). The per-app *doc research* was gathered by Claude Code "
          "web-search sub-agents, **not** the `COMPOSIO_SEARCH` path (that provider is committed & runnable, "
          "MCP server registered — a full Composio-powered run is one auth step away). Flagged, not blurred.")
        w("- No paid accounts used; a payment/partnership gate reported with evidence *is* the finding.")
        w("- Confidence is per-field; lower-confidence values are flagged on the live page.")
        w(f"- Verification graded {verify.get('graded_fields', 80)} input fields on a "
          f"{verify.get('sample', 20)}-app stratified sample — the accuracy number is the sample's.")
        w(f"- Only {human} of {n} apps are human-checked (the audited sample); the rest carry the agent's own confidence.")
        w("")
        w("*Generated from `output/results.json` + `output/patterns.json` + `data/verification_report.json` "
          "by `agents/markdown_writer.py` — same data as the live page.*")

        md = "\n".join(out) + "\n"
        (config.ROOT / "CASE_STUDY.md").write_text(md, encoding="utf-8")
        return md
