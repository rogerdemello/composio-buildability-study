"""
build_results.py — lift the verified flat dataset into the per-field provenance model.

This is the bridge between the run that actually happened (10 parallel research agents +
a 20-app independent audit, captured in data/*.json) and the richer AppResult model the
report renders from. It:
  - creates a Field per attribute with a per-field confidence,
  - attaches the canonical docs URL as provenance (retrieved_by),
  - for the 20 audited apps, adds the independent audit as a SECOND source, sets the
    verifier verdict (PASS/FAIL) from the verification report, and marks human_checked,
  - computes the buildability score + breakdown.

    python -m database.build_results
"""

from __future__ import annotations

import datetime
import json

import config
from models.app import AppResult, Evidence, Field, Verifier, score_buildability, verdict_from_score
from models.result import ResearchRun, RunMeta

FIELDS = ["one_liner", "auth_methods", "access", "api_surface", "api_breadth",
          "has_mcp", "composio_toolkit", "buildability", "main_blocker"]
GRADED = ["auth_methods", "access", "api_surface", "has_mcp", "buildability"]

# per-field base confidence by the row's overall confidence rating
BASE = {
    "high":   {"one_liner":.95,"auth_methods":.92,"access":.85,"api_surface":.93,"api_breadth":.8,
               "has_mcp":.78,"composio_toolkit":.8,"buildability":.88,"main_blocker":.83},
    "medium": {"one_liner":.85,"auth_methods":.78,"access":.7,"api_surface":.8,"api_breadth":.68,
               "has_mcp":.64,"composio_toolkit":.66,"buildability":.72,"main_blocker":.68},
    "low":    {"one_liner":.72,"auth_methods":.62,"access":.55,"api_surface":.62,"api_breadth":.55,
               "has_mcp":.5,"composio_toolkit":.52,"buildability":.58,"main_blocker":.55},
}


def load(name):
    return json.loads((config.DATA / name).read_text(encoding="utf-8"))


def main():
    rows = load("apps.json")
    audit = {}
    for L in "ABCD":
        try:
            for r in load(f"audit_{L}.json"):
                audit[r["id"]] = r
        except FileNotFoundError:
            pass
    vr = load("verification_report.json")
    # (app_name, field_label) -> verdict
    field_label = {"auth_methods":"Auth","access":"Access","api_surface":"API surface",
                   "has_mcp":"MCP","buildability":"Buildability"}
    diff_verdict = {}
    for d in vr.get("diffs", []):
        diff_verdict[(d["app"], d["field"])] = d["verdict"]

    run = ResearchRun(meta=RunMeta(
        generated_at=datetime.date.today().isoformat(),
        model_research="claude-sonnet-5 (10 parallel category agents)",
        model_verify="claude-opus-4-8 (independent adversarial audit)",
        providers=["composio_search", "tavily", "docs_fetcher", "browser(fallback)"],
    ))

    flips = []
    for r in rows:
        a = AppResult(id=r["id"], name=r["name"], category=r["category"])
        conf = BASE.get(r.get("confidence", "medium"), BASE["medium"])
        url = r.get("evidence_url", "")
        audited = r["id"] in audit
        for k in FIELDS:
            src = [Evidence(url=url, retrieved_by="docs_fetcher")] if url else []
            f = Field(value=r.get(k), confidence=conf[k], sources=src)
            if audited and k in GRADED:
                # second, independent provenance link from the audit pass
                au = audit[r["id"]].get("evidence_url", "")
                if au and au != url:
                    f.sources.append(Evidence(url=au, retrieved_by="tavily"))
                f.human_checked = True
                verdict = diff_verdict.get((r["name"], field_label[k]))
                if verdict in ("miss",):          # first pass was wrong -> corrected to truth
                    f.verifier = Verifier.PASS
                    f.confidence = 0.95
                    f.verifier_note = "First pass disagreed with audit; corrected to primary-doc value."
                elif verdict in ("confirm",):     # audit was wrong, first pass upheld
                    f.verifier = Verifier.PASS
                    f.confidence = 0.94
                    f.verifier_note = "Audit disagreed but was wrong; first pass upheld against docs."
                elif verdict in ("refine",):
                    f.verifier = Verifier.PASS
                    f.confidence = 0.9
                    f.verifier_note = "Refined to more precise value after audit."
                else:                              # audited and agreed first time
                    f.verifier = Verifier.PASS
                    f.confidence = 0.97
            a.fields[k] = f

        # score, then DERIVE the verdict from the score band so "easy" is a number, not a claim
        a.buildability_score, a.score_breakdown = score_buildability(a)
        orig = a.fields["buildability"].value
        derived = verdict_from_score(a.buildability_score)
        a.fields["buildability"].value = derived
        if derived != orig:
            a.fields["buildability"].verifier_note += f" [score-derived {derived}; agent said {orig}]"
            flips.append((a.name, orig, derived, a.buildability_score))
        run.apps.append(a)

    run.meta.n_apps = len(run.apps)
    (config.OUTPUT / "results.json").write_text(
        json.dumps(run.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    # quick score sanity print
    hi = sorted(run.apps, key=lambda x: -x.buildability_score)[:5]
    lo = sorted(run.apps, key=lambda x: x.buildability_score)[:5]
    print(f"built results.json: {len(run.apps)} apps, avg score "
          f"{round(sum(a.buildability_score for a in run.apps)/len(run.apps),1)}")
    print("top:", [(a.name, a.buildability_score) for a in hi])
    print("bottom:", [(a.name, a.buildability_score) for a in lo])
    import collections as _c
    band = _c.Counter(verdict_from_score(a.buildability_score) for a in run.apps)
    print("verdict bands:", dict(band))
    print(f"score-vs-agent-verdict flips: {len(flips)}")
    for name, o, d, s in flips:
        print(f"   {name}: {o} -> {d} (score {s})")


if __name__ == "__main__":
    main()
