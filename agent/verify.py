"""
verify.py — the accuracy loop.

Two independent checks, deliberately NOT the same path that produced the data:

1. Independent re-research (agent cross-check)
   Re-research a sampled app from scratch with a *different* model/prompt and a
   skeptic system prompt, then diff the disputed fields against the first pass.
   Disagreements are flagged for a human, never auto-overwritten.

2. Evidence liveness (browser-use / fetch check)
   Fetch every sampled row's evidence_url and confirm it resolves (200) and the
   page actually mentions "API"/"developer"/auth terms — catches hallucinated or
   stale doc links, the most common failure mode of research agents.

The human then adjudicates the flagged rows. `apply_corrections()` records the
before/after so the case study can show accuracy moving from first pass -> verified.

Run:
    python -m agent.verify --sample 20          # stratified sample across categories
    python -m agent.verify --ids 4,15,50,84
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import urllib.request

from .schema import validate_record

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MODEL_VERIFY = os.environ.get("VERIFY_MODEL", "claude-opus-4-8")  # stronger model to audit

# Fields we hold the agent accountable for (the ones that drive a build decision).
GRADED_FIELDS = ["auth_methods", "access", "api_surface", "has_mcp", "buildability"]

SKEPTIC_SYSTEM = """You are an adversarial fact-checker auditing another agent's research.
Assume the prior answer may be wrong. Independently read the official docs and decide each
graded field yourself. Do not anchor on the prior values. If the docs are ambiguous, say so.
Return your own record via emit_record; set confidence based only on what you personally verified."""


def stratified_sample(rows: list[dict], n: int) -> list[dict]:
    """Pick ~n rows spread across categories so the sample isn't all easy apps."""
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    out, i = [], 0
    cats = sorted(by_cat)
    while len(out) < n and any(by_cat.values()):
        c = cats[i % len(cats)]
        if by_cat[c]:
            out.append(by_cat[c].pop(0))
        i += 1
    return out


def check_evidence_url(url: str, timeout: int = 15) -> dict:
    """Liveness + relevance check on an evidence link (the browser-use stand-in)."""
    result = {"url": url, "ok": False, "status": None, "relevant": None}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 composio-verify"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result["status"] = resp.status
            body = resp.read(200_000).decode("utf-8", "ignore").lower()
            result["ok"] = 200 <= resp.status < 400
            result["relevant"] = any(k in body for k in ("api", "developer", "oauth", "token", "endpoint"))
    except Exception as e:
        result["error"] = str(e)
    return result


def field_diff(first: dict, audit: dict) -> dict:
    """Return the graded fields where the audit disagrees with the first pass."""
    disagreements = {}
    for f in GRADED_FIELDS:
        a, b = first.get(f), audit.get(f)
        if isinstance(a, list):
            a, b = sorted(a or []), sorted(b or [])
        if a != b:
            disagreements[f] = {"first_pass": first.get(f), "audit": audit.get(f)}
    return disagreements


def run(sample_ids: list[int] | None, sample_n: int) -> dict:
    rows = json.loads((DATA / "apps.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rows}
    sample = [by_id[i] for i in sample_ids] if sample_ids else stratified_sample(list(rows), sample_n)

    from anthropic import Anthropic
    from .research_agent import build_composio, research_one, _emit_tool  # reuse loop, swap system
    import agent.research_agent as ra
    ra.SYSTEM = SKEPTIC_SYSTEM
    ra.MODEL = MODEL_VERIFY

    client = Anthropic()
    composio, tools = build_composio()

    report = {"checked": len(sample), "rows": []}
    for app in sample:
        audit = research_one(client, composio, tools, app)
        entry = {
            "id": app["id"], "name": app["name"],
            "evidence_check": check_evidence_url(app.get("evidence_url", "")),
            "disagreements": field_diff(app, audit),
            "audit_confidence": audit.get("confidence"),
        }
        report["rows"].append(entry)

    # Accuracy = fields where first pass and independent audit agree, over graded fields checked.
    graded = sum(len(GRADED_FIELDS) for _ in sample)
    disagreed = sum(len(r["disagreements"]) for r in report["rows"])
    report["field_accuracy"] = round((graded - disagreed) / graded, 3) if graded else None
    report["evidence_live_rate"] = round(
        sum(1 for r in report["rows"] if r["evidence_check"].get("ok")) / len(sample), 3
    ) if sample else None

    (DATA / "verification_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"field_accuracy={report['field_accuracy']}  evidence_live={report['evidence_live_rate']}")
    print(f"-> {DATA / 'verification_report.json'}")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated ids to verify")
    ap.add_argument("--sample", type=int, default=20)
    args = ap.parse_args()
    ids = [int(x) for x in args.ids.split(",")] if args.ids else None
    run(ids, args.sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
