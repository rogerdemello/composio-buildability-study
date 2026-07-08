"""
analyze.py — consolidate category files into the master dataset and compute patterns.

    python -m agent.analyze consolidate   # data/cat_*.json  -> data/apps.json
    python -m agent.analyze patterns       # data/apps.json    -> data/patterns.json (+ prints headline)
"""

from __future__ import annotations

import collections
import json
import pathlib
import sys

from .schema import validate_record

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def consolidate() -> None:
    rows: list[dict] = []
    for n in range(1, 11):
        f = DATA / f"cat_{n}.json"
        if not f.exists():
            print(f"  WARN missing {f.name}", file=sys.stderr)
            continue
        rows.extend(json.loads(f.read_text(encoding="utf-8")))
    rows.sort(key=lambda r: r["id"])
    bad = {r["id"]: validate_record(r) for r in rows}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        print(f"  validation issues on ids: {bad}", file=sys.stderr)
    (DATA / "apps.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"consolidated {len(rows)} rows -> data/apps.json")


def _count(rows, key):
    c = collections.Counter()
    for r in rows:
        v = r.get(key)
        if isinstance(v, list):
            for x in v:
                c[x] += 1
        else:
            c[str(v)] += 1
    return dict(c.most_common())


def patterns() -> dict:
    rows = json.loads((DATA / "apps.json").read_text(encoding="utf-8"))
    n = len(rows)

    # gating rollup: self-serve+trial+waitlist are "obtainable"; the rest are "gated"
    obtainable = {"self-serve", "sandbox-self-serve", "trial-only", "waitlist"}
    gated = [r for r in rows if r["access"] not in obtainable]

    by_cat_build = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        by_cat_build[r["category"]][r["buildability"]] += 1

    out = {
        "n": n,
        "auth": _count(rows, "auth_methods"),
        "access": _count(rows, "access"),
        "api_surface": _count(rows, "api_surface"),
        "mcp": _count(rows, "has_mcp"),
        "composio_toolkit": _count(rows, "composio_toolkit"),
        "buildability": _count(rows, "buildability"),
        "confidence": _count(rows, "confidence"),
        "gated_count": len(gated),
        "gated_apps": [r["name"] for r in gated],
        "blocked_apps": [r["name"] for r in rows if r["buildability"] == "blocked"],
        "easy_apps": [r["name"] for r in rows if r["buildability"] == "easy"],
        "by_category_buildability": {k: dict(v) for k, v in by_cat_build.items()},
        "blockers": _count([r for r in rows if r["buildability"] != "easy"], "main_blocker"),
    }
    (DATA / "patterns.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print("== HEADLINE PATTERNS ==")
    print(f"auth:         {out['auth']}")
    print(f"access:       {out['access']}")
    print(f"buildability: {out['buildability']}")
    print(f"mcp:          {out['mcp']}")
    print(f"composio:     {out['composio_toolkit']}")
    print(f"blocked:      {out['blocked_apps']}")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "consolidate"
    if cmd == "consolidate":
        consolidate()
    elif cmd == "patterns":
        patterns()
    else:
        print("usage: analyze.py [consolidate|patterns]")
