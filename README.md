# Composio App-Research Agent

> Take-home for the Composio **AI Product Ops** role. Research the developer/API posture of
> 100 apps — auth, self-serve vs gated, API surface, MCP, buildability — **with an agent, not by hand**,
> then find the patterns and **prove the findings are trustworthy** with a verification loop.

**📊 Live case study:** https://rogerdemello.github.io/composio-buildability-study/
**📦 This repo:** the research agent, the verification loop, and the raw data behind the page.

---

## TL;DR of the findings (n = 100)

- **OAuth2 dominates auth** (64/100), almost always paired with a simpler API-key or token path (42 + 41). **Basic is nearly extinct** (12, mostly legacy).
- **77 of 100 let a developer self-serve credentials** (self-serve / sandbox / trial). **61 are buildable today** ("easy"), 32 with friction, **only 7 fully blocked**.
- **The blockers cluster, they don't scatter:** the wall is almost always *contact-sales / enterprise gating* (DealCloud, Gladly, SFCC, PitchBook, Clay) or *approval reviews* (ad platforms, Amazon SP-API, WhatsApp) — **not a missing API**. That's the "needs outreach" pile.
- **MCP has gone mainstream:** 40 apps ship an **official** MCP server and 32 more have community ones — 72/100 are already MCP-reachable, concentrated in Dev/Infra and Productivity.
- **Composio already covers 56/100;** the 37 "no" rows are the clearest toolkit-expansion opportunities.

Exact numbers, the full 100-row matrix, and the honest hit/miss verification are on the case-study page.

---

## How it works

```
data/apps_input.json ──► research_agent.py ──► data/cat_*.json ──► analyze.py ──► data/apps.json
        (100 apps)         (Claude + Composio        (per-batch)      consolidate      (master)
                            search/scrape tools)                                          │
                                                                                          ▼
                                                          verify.py ◄──────────── data/patterns.json
                                                     (independent audit +          (clustered insight)
                                                      evidence liveness)
                                                                │
                                                                ▼
                                                    data/verification_report.json
```

### 1. The research agent (`agent/research_agent.py`)
For each app it runs a short **agentic loop**: Claude + **Composio's own `COMPOSIO_SEARCH` tools**
find and read the official developer docs, then a forced-tool call emits one structured record
against `agent/schema.py`. Using Composio's SDK to build the researcher is deliberate — it dogfoods
the exact primitive Composio ships to customers.

Every record captures: category + one-liner, auth method(s), access model (self-serve vs the specific
gate), API surface + breadth, MCP status, whether Composio already has a toolkit, a buildability
verdict + main blocker, an **evidence URL**, and a **confidence** rating.

### 2. Pattern analysis (`agent/analyze.py`)
Consolidates the per-category files into `data/apps.json`, validates every row against the schema,
and clusters the results into `data/patterns.json` (auth mix, gating split, blocker frequency,
buildability by category, MCP/Composio coverage).

### 3. The verification loop (`agent/verify.py`) — *this is the point*
Accuracy is graded, not asserted. On a **stratified sample** across all 10 categories:
- **Independent re-research** — a *different, stronger* model with an adversarial "assume this is wrong"
  system prompt re-derives the graded fields from scratch and **diffs** against the first pass.
- **Evidence liveness** — every sampled `evidence_url` is fetched and checked for a live 200 and
  developer-relevant content, catching hallucinated or stale links.

Disagreements are **flagged for a human, never auto-overwritten**. The report records
`field_accuracy` and `evidence_live_rate` so the case study can show accuracy moving from the
first pass to the verified number — and the misses are shown honestly.

---

## Where a human was needed

The agent is strong on well-documented apps and honest about weak ones (it downgrades confidence),
but a human had to adjudicate:
- **Login-gated / thin docs** (fanbasis, iPayX, Paygent, higgsfield) — the agent can't read behind a login wall.
- **Sandbox-vs-production splits** in fintech — "self-serve sandbox, gated production (KYC)" is a judgment call.
- **Composio-catalog stubs** — a toolkit *page* existing with 0 tools is *not* real coverage; a human sets the call.
- **"Blocked" vs "moderate"** on enterprise apps where a partner path may exist but isn't self-serve.

These are exactly the rows the verification loop targets first.

---

## Run it yourself

```bash
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY and COMPOSIO_API_KEY

# 1. research (all 100, or a subset)
python -m agent.research_agent                 # full run
python -m agent.research_agent --ids 1,4,55    # a few apps
python -m agent.research_agent --category "Ecommerce"

# 2. consolidate + patterns
python -m agent.analyze consolidate
python -m agent.analyze patterns

# 3. verify a sample and grade accuracy
python -m agent.verify --sample 20
```

> The committed `data/*.json` is the run behind the published case study, so you can inspect the
> findings without any API keys. Re-running the agent will refresh them.

---

## Layout

```
composio/
├─ agent/
│  ├─ research_agent.py   # the researcher (Claude + Composio tools, forced structured output)
│  ├─ verify.py           # independent-audit + evidence-liveness accuracy loop
│  ├─ analyze.py          # consolidate + cluster into patterns
│  └─ schema.py           # record schema, controlled vocab, buildability rubric, validator
├─ data/
│  ├─ apps_input.json     # the 100 apps (input)
│  ├─ cat_1..10.json      # per-category agent output
│  ├─ apps.json           # consolidated master dataset (100 rows)
│  ├─ patterns.json       # clustered insights
│  └─ verification_report.json
├─ web/
│  └─ index.html          # the self-contained case study (deployed)
├─ requirements.txt
└─ .env.example
```

## Honesty notes

- I did **not** use paid accounts. Where an app is gated behind payment/partnership, that finding
  *is the answer* — reported with evidence, not treated as a failure.
- Confidence is set per row; low-confidence rows are called out on the page, not hidden.
- The verification sample is a sample, not all 100 — the page states the sample size and what it implies.
