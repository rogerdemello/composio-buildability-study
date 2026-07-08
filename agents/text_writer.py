"""Plain-text case study (CASE_STUDY.txt) for pasting into Word/Docs.

Same JSON source as the HTML/Markdown; ASCII-clean, no markdown symbols, so it
reads correctly when copy-pasted into a word processor.
"""

from __future__ import annotations

import collections
import json

import config

CAT_ORDER = [
    "CRM and Sales", "Support and Helpdesk", "Communications and Messaging",
    "Marketing, Ads, Email and Social", "Ecommerce", "Data, SEO and Scraping",
    "Developer, Infra and Data platforms", "Productivity and Project Management",
    "Finance and Fintech", "AI, Research and Media-native",
]


def _verdict(s: int) -> str:
    return "easy" if s >= 68 else "moderate" if s >= 34 else "blocked"


class TextWriter:
    def __init__(self, repo_url="https://github.com/rogerdemello/composio-buildability-study",
                 live_url="https://rogerdemello.github.io/composio-buildability-study/"):
        self.repo_url, self.live_url = repo_url, live_url

    def build(self) -> str:
        apps = json.loads((config.OUTPUT / "results.json").read_text(encoding="utf-8"))["apps"]
        pat = json.loads((config.OUTPUT / "patterns.json").read_text(encoding="utf-8"))
        ver = json.loads((config.DATA / "verification_report.json").read_text(encoding="utf-8"))
        comp = json.loads((config.OUTPUT / "composio_catalog_check.json").read_text(encoding="utf-8"))
        C = pat.get("counts", {})
        fv = lambda a, k: a["fields"][k]["value"]  # noqa: E731

        n = len(apps)
        n_easy = sum(1 for a in apps if a["buildability_score"] >= 68)
        n_mod = sum(1 for a in apps if 34 <= a["buildability_score"] < 68)
        n_blk = n - n_easy - n_mod
        avg = round(sum(a["buildability_score"] for a in apps) / n)

        L = []
        def line(s=""): L.append(s)
        def head(s):
            line(); line(s.upper()); line("=" * len(s))
        def sub(s):
            line(); line(s); line("-" * len(s))

        # ---- title ----
        line("COMPOSIO - 100-APP AGENT-TOOLKIT BUILDABILITY STUDY")
        line("=" * 52)
        line("AI Product Ops take-home - case study")
        line()
        line("An async agent pipeline researched 100 apps against their live developer")
        line("docs, scored each app's buildability, and attached evidence + confidence to")
        line("every field. An independent agent then audited a sample to prove the numbers.")
        line()
        line("Live case study : " + self.live_url)
        line("Source repo     : " + self.repo_url)
        line()
        line("At a glance: %d apps | 10 categories | avg buildability score %d/100 | "
             "accuracy %d%%->%d%% verified" % (n, avg, ver["before"], ver["after"]))

        # ---- headline ----
        head("1. The headline")
        line("THE ONE-SENTENCE FINDING:")
        for chunk in _wrap(pat["headline"]):
            line("  " + chunk)
        line()
        for i, ins in enumerate(pat.get("insights", []), 1):
            line("%02d. %s" % (i, ins["title"]))
            for chunk in _wrap(ins["detail"], width=88):
                line("    " + chunk)
            line()

        head("2. Key numbers")
        line("  Buildable today (score >= 68) ....... %d / %d" % (n_easy, n))
        line("  Buildable with friction (34-67) ..... %d / %d" % (n_mod, n))
        line("  Blocked (< 34) ...................... %d / %d" % (n_blk, n))
        line("  Developer can self-serve creds ...... %d / %d" % (C.get("self_serve", 0), n))
        line("  Ship an official MCP server ......... %d / %d" % (C.get("mcp", {}).get("official", 0), n))
        line("  Already a Composio toolkit .......... %d / %d" % (C.get("composio", {}).get("yes", 0), n))

        # ---- patterns ----
        head("3. The patterns")
        def dist(title, d):
            sub(title)
            for k, v in d.items():
                line("  %-20s %s %d" % (k, "#" * round(24 * v / (max(d.values()) or 1)), v))
        dist("Auth methods (apps support more than one)", C.get("auth", {}))
        dist("Access - can a developer self-serve credentials?", C.get("access", {}))
        dist("API surface", C.get("api_surface", {}))
        dist("MCP availability", C.get("mcp", {}))

        sub("Buildability by category (easy / moderate / blocked, out of 10)")
        by = collections.defaultdict(lambda: collections.Counter())
        for a in apps:
            by[a["category"]][_verdict(a["buildability_score"])] += 1
        for cat in CAT_ORDER:
            c = by[cat]
            line("  %-42s %d / %d / %d" % (cat, c["easy"], c["moderate"], c["blocked"]))

        sub("Easy wins (just build it)")
        for chunk in _wrap(", ".join(pat.get("easy_wins", [])), width=90):
            line("  " + chunk)
        sub("Needs outreach (gated behind sales / approval / partnership)")
        for chunk in _wrap(", ".join(pat.get("needs_outreach", [])), width=90):
            line("  " + chunk)
        sub("Surprises")
        for s in pat.get("surprises", []):
            for j, chunk in enumerate(_wrap(s, width=88)):
                line(("  - " if j == 0 else "    ") + chunk)

        # ---- the 100 ----
        head("4. The 100 apps")
        line("Format:  App  ->  auth | access | api | mcp | composio | score/100 (verdict)")
        line("Score is the quantified verdict; gated access is hard-capped so a strong API you")
        line("cannot get credentials for cannot score 'easy'. [H] = human-checked (audited sample).")
        for cat in CAT_ORDER:
            sub(cat)
            for a in sorted([x for x in apps if x["category"] == cat], key=lambda x: x["id"]):
                hc = " [H]" if any(f["human_checked"] for f in a["fields"].values()) else ""
                auth = "+".join(fv(a, "auth_methods") or [])
                sc = a["buildability_score"]
                line("  %2d. %-26s -> %-14s | %-18s | %-12s | %-9s | composio:%-3s | %d (%s)%s" % (
                    a["id"], a["name"], auth, fv(a, "access"), fv(a, "api_surface"),
                    fv(a, "has_mcp"), fv(a, "composio_toolkit"), sc, _verdict(sc), hc))

        # ---- agent ----
        head("5. The agent that did it")
        line("A modular pipeline built on Composio's own SDK + search tools:")
        line()
        line("  providers  : composio_search -> tavily -> firecrawl -> docs_fetcher -> browser*")
        line("               (* Playwright browser is a fallback, only when docs are JS-walled)")
        line("  researcher : each app -> a structured record where every FIELD carries its own")
        line("               value + confidence + evidence URL (async, Semaphore(5), resumable)")
        line("  verifier   : a different, stronger model re-checks a sample adversarially, and")
        line("               every evidence URL is fetched for a live 200")
        line("  patterns   : an LLM reads the whole dataset for the insights above,")
        line("               grounded in code-computed counts so it cannot invent a number")
        line("  writers    : the HTML page, this text, and the Markdown are all rendered from JSON")

        head("6. How Composio was used (and where it was not)")
        line("USED FOR REAL - verifying the 'composio_toolkit' column:")
        line("  database/verify_composio.py pulls Composio's live catalog through the Composio")
        line("  SDK (composio.toolkits.get(), 1000+ toolkits) plus per-slug API checks, and")
        line("  cross-checks every app's composio_toolkit value. It reached %s%% agreement with" % comp.get("agreement_pct"))
        line("  Composio's catalog and corrected 4 rows the research LLM got wrong")
        line("  (Twilio, Clay, Devin -> no; GoHighLevel -> yes).")
        line()
        line("NOT THE COMPOSIO PATH (yet) - the doc research:")
        line("  The per-app auth/access/API/MCP research was gathered by the same agent")
        line("  structure running as Claude Code web-search sub-agents, not Composio's")
        line("  COMPOSIO_SEARCH tool. That provider (providers/composio_search.py) is committed")
        line("  and runnable, and the Composio MCP server is registered - a full Composio-powered")
        line("  research run is one auth step away. Flagged here, not blurred.")

        head("7. Where a human was needed")
        for b in [
            "Login-gated / thin docs (fanbasis, iPayX, Paygent, higgsfield) - the agent cannot "
            "read behind a login wall, so it downgraded confidence and a human made the call.",
            "Sandbox vs production fintech splits ('sandbox-self-serve') - a judgment the rubric "
            "could not fully encode.",
            "Composio catalog stubs - a toolkit page with 0 tools is not real coverage.",
            "Access reclassification - the score exposed hedged 'moderate' calls that were really "
            "gated (SFCC, Brex) or really self-serve; a human set the access value the score keys off.",
        ]:
            for j, chunk in enumerate(_wrap(b, width=88)):
                line(("  - " if j == 0 else "    ") + chunk)

        head("8. How it was built")
        line("  1. Perfect on 5, then scale. Tuned on 5 golden apps across five auth models")
        line("     (Salesforce, HubSpot, Slack, Stripe, Shopify), then scaled to 100.")
        line("  2. Async fan-out under Semaphore(5), resumable so a crash never re-does work.")
        line("  3. Score, don't guess - buildability is a weighted 0-100 score; verdict = band.")
        line("  4. Verify + lift - independent audit + evidence-liveness moved accuracy up.")

        # ---- verification ----
        head("9. Is it trustworthy?")
        line("Graded input-field accuracy on the sample:  %d%%  ->  %d%%" % (ver["before"], ver["after"]))
        line()
        for chunk in _wrap(_plain(ver["explain"]), width=90):
            line(chunk)
        line()
        line("Checks:")
        for m in ver.get("metrics", []):
            line("  - " + _plain(m))
        sub("Hits and misses (shown honestly)")
        line("  %-26s %-14s %-22s %-22s %s" % ("App", "Field", "First pass", "Verified", "Verdict"))
        for d in ver.get("diffs", []):
            line("  %-26s %-14s %-22s %-22s %s" % (
                d["app"][:26], d["field"][:14], str(d["first"])[:22], str(d["verified"])[:22], d["verdict"]))
        line()
        line("  (miss = first pass wrong, fixed | confirm = auditor wrong, first pass upheld |")
        line("   refine = both defensible, more precise value adopted)")

        head("10. What defeated the agent")
        for nm, tx in [
            ("Paygent Connect", "Genuinely defeated us. Japanese, contract-only, mutual-TLS certificates, "
             "no self-serve. The brief's 'NMI-powered' hint appears wrong; we report that rather than guess."),
            ("NotebookLM", "No standalone public API - only a licensed enterprise API on Google Cloud. "
             "A valid 'blocked' finding, not a gap in the research."),
            ("fanbasis / iPayX", "Core developer docs sit behind a login wall; read the public reference, "
             "flagged low confidence."),
            ("higgsfield", "Thin, fast-moving docs; real self-serve REST API confirmed but breadth "
             "uncertain -> mid-band score."),
        ]:
            line("  %s:" % nm)
            for chunk in _wrap(tx, width=86):
                line("    " + chunk)

        head("11. Run it yourself")
        line("  pip install -r requirements.txt")
        line("  cp .env.example .env      # set NVIDIA_API_KEY (default backend)")
        line()
        line("  python main.py research --golden   # perfect the pipeline on 5 apps")
        line("  python main.py research            # scale to all 100 (async, resumable)")
        line("  python main.py verify --sample 20  # independent audit + accuracy")
        line("  python main.py patterns            # LLM pattern engine")
        line("  python main.py report              # render the HTML page")
        line("  python main.py md                  # render the Markdown case study")
        line("  python -m database.verify_composio # ground-truth the toolkit column via Composio SDK")

        head("12. Honesty notes")
        for b in [
            "No paid accounts were used. A payment/partnership gate reported with evidence IS the finding.",
            "Confidence is per field, not per app; lower-confidence values are flagged on the live page.",
            "Verification graded %d input fields on a %d-app stratified sample - the accuracy number is "
            "the sample's." % (ver.get("graded_fields", 80), ver.get("sample", 20)),
            "Only the audited sample is human-checked; the rest carry the agent's own confidence. "
            "That distinction is shown, not blurred.",
        ]:
            for j, chunk in enumerate(_wrap(b, width=90)):
                line(("  - " if j == 0 else "    ") + chunk)
        line()
        line("Generated from output/results.json + output/patterns.json + verification data")
        line("by agents/text_writer.py - the same source as the live page.")

        txt = "\n".join(L) + "\n"
        (config.ROOT / "CASE_STUDY.txt").write_text(txt, encoding="utf-8")
        return txt


def _wrap(s: str, width: int = 92) -> list[str]:
    import textwrap
    return textwrap.wrap(s, width=width) or [""]


def _plain(s: str) -> str:
    return s.replace("<b>", "").replace("</b>", "").replace("**", "")


if __name__ == "__main__":
    TextWriter().build()
    print("wrote CASE_STUDY.txt")
