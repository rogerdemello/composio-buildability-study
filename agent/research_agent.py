"""
research_agent.py — the app-research agent.

For each app it runs a short agentic loop:
  Claude  +  Composio's own search/scrape tools  ->  fetch live docs
  -> then a forced structured-output step that fills RECORD_SCHEMA.

Using Composio's SDK + tools to build the researcher is deliberate: it is the
same primitive Composio ships to customers, so the pipeline dogfoods the product.

Run:
    python -m agent.research_agent                 # research all 100
    python -m agent.research_agent --ids 1,4,55    # research a subset
    python -m agent.research_agent --category "Ecommerce"

Env (.env):
    ANTHROPIC_API_KEY=...
    COMPOSIO_API_KEY=...          # for Composio search/scrape tools
    RESEARCH_MODEL=claude-sonnet-5 (default)
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

from .schema import RECORD_SCHEMA, BUILDABILITY_RUBRIC, validate_record

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-5")
USER_ID = os.environ.get("COMPOSIO_USER_ID", "default")

SYSTEM = f"""You are a Composio product-ops research agent. Your job: for a single app,
determine its developer/API posture and return one structured record.

Work like an analyst, not a guesser:
- Use the search/scrape tools to find the OFFICIAL developer docs and read them.
- Prefer primary sources (the vendor's own docs) over blog posts.
- Only claim confidence "high" when a fact came from an official docs page you actually read.
- "No public API", "gated behind partnership", or "waitlist" are VALID, valuable findings — not failures.
- Capture sandbox-vs-production splits for fintech (e.g. "sandbox self-serve, production gated-approval").

Buildability rubric (score exactly this way):
{BUILDABILITY_RUBRIC}
"""

STRUCT_INSTRUCTION = """Now emit the final record by calling the `emit_record` tool exactly once.
Fill every field. Keep one_liner <=12 words. evidence_url must be the canonical docs URL you actually read.
Set confidence honestly based on how much you could verify from primary docs."""


def _emit_tool() -> dict:
    """The forced structured-output tool. Its input schema IS the record schema."""
    return {
        "name": "emit_record",
        "description": "Emit the final structured research record for this app.",
        "input_schema": RECORD_SCHEMA,
    }


def build_composio():
    """Bind Composio's search/scrape toolkit through the Anthropic provider.

    We ask for COMPOSIO_SEARCH (Composio's hosted web-search/Tavily tool) and, if
    available on the account, a scraping toolkit. These are Composio's OWN tools —
    the researcher is itself an agent built on Composio.
    """
    from composio import Composio
    from composio_anthropic import AnthropicProvider

    composio = Composio(provider=AnthropicProvider())
    toolkits = ["COMPOSIO_SEARCH"]  # add "FIRECRAWL" if enabled on the account
    tools = composio.tools.get(user_id=USER_ID, toolkits=toolkits)
    return composio, tools


def research_one(anthropic_client, composio, tools, app: dict, max_turns: int = 6) -> dict:
    """Run the agentic loop for one app and return a validated record dict."""
    messages = [{
        "role": "user",
        "content": (
            f"Research this app for a Composio toolkit assessment.\n\n"
            f"App: {app['name']}\nCategory: {app['category']}\nHint: {app.get('hint','')}\n\n"
            "Answer: category one-liner; auth method(s); access model (self-serve vs gated, and how); "
            "API surface (REST/GraphQL/etc + breadth); whether an official or community MCP server exists; "
            "whether Composio already has a toolkit for it (check docs.composio.dev); buildability verdict + main blocker; "
            "and the canonical docs URL as evidence.\n"
            "Use the search/scrape tools first, then stop and prepare the record."
        ),
    }]

    # --- Phase 1: agentic research (tool calls resolved by Composio) ---
    for _ in range(max_turns):
        resp = anthropic_client.messages.create(
            model=MODEL, max_tokens=2048, system=SYSTEM, tools=tools, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            break
        # Composio executes the tool calls and appends tool results for us.
        tool_results = composio.provider.handle_tool_calls(response=resp, user_id=USER_ID)
        messages.append({"role": "user", "content": tool_results})

    # --- Phase 2: force the structured record ---
    messages.append({"role": "user", "content": STRUCT_INSTRUCTION})
    resp = anthropic_client.messages.create(
        model=MODEL, max_tokens=1500, system=SYSTEM,
        tools=[_emit_tool()], tool_choice={"type": "tool", "name": "emit_record"},
        messages=messages,
    )
    record = next(b.input for b in resp.content if getattr(b, "type", None) == "tool_use")
    record["id"], record["name"], record["category"] = app["id"], app["name"], app["category"]

    problems = validate_record(record)
    if problems:
        record["_validation"] = problems  # surfaced, never silently dropped
    return record


def load_apps() -> list[dict]:
    return json.loads((DATA / "apps_input.json").read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated app ids to research")
    ap.add_argument("--category", help="only research this category")
    ap.add_argument("--out", default=str(DATA / "apps.json"))
    args = ap.parse_args()

    apps = load_apps()
    if args.ids:
        want = {int(x) for x in args.ids.split(",")}
        apps = [a for a in apps if a["id"] in want]
    if args.category:
        apps = [a for a in apps if a["category"] == args.category]

    try:
        from anthropic import Anthropic
    except ImportError:
        print("pip install -r requirements.txt first", file=sys.stderr)
        return 1

    anthropic_client = Anthropic()
    composio, tools = build_composio()

    out_path = pathlib.Path(args.out)
    existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else []
    by_id = {r["id"]: r for r in existing}

    for i, app in enumerate(apps, 1):
        print(f"[{i}/{len(apps)}] researching {app['name']} ...", flush=True)
        try:
            rec = research_one(anthropic_client, composio, tools, app)
            by_id[rec["id"]] = rec
        except Exception as e:  # never let one app kill the batch
            print(f"  !! {app['name']} failed: {e}", file=sys.stderr)
            by_id.setdefault(app["id"], {**app, "confidence": "low", "_error": str(e)})
        out_path.write_text(
            json.dumps([by_id[k] for k in sorted(by_id)], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        time.sleep(0.5)  # be polite to the search tool

    print(f"done -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
