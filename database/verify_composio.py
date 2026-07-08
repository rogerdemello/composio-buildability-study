"""
verify_composio.py — use Composio's OWN SDK to ground-truth the `composio_toolkit` column.

This is a genuine use of Composio in the pipeline: it pulls the live toolkit catalog
via the Composio SDK and cross-checks every app's `composio_toolkit` value against it,
so that column is verified against Composio itself rather than asserted by the research LLM.

    python -m database.verify_composio        # writes output/composio_catalog_check.json
"""

from __future__ import annotations

import json
import os
import re

import config


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


# our app name -> extra candidate slugs Composio might use
ALIASES = {
    "Zoho CRM": ["zoho", "zohocrm"], "Zoho Cliq": ["zohocliq", "cliq"],
    "Monday.com": ["monday"], "Google Ads": ["googleads", "google_ads"],
    "Meta Ads": ["facebook", "meta", "facebookads"], "LinkedIn Ads": ["linkedin"],
    "WhatsApp Business": ["whatsapp"], "Help Scout": ["helpscout"],
    "Lark (Larksuite)": ["lark", "larksuite"], "Threads (Meta)": ["threads"],
    "Magento (Adobe Commerce)": ["magento", "adobecommerce"],
    "Amazon Selling Partner": ["amazonsellingpartner", "sellingpartner"],  # generic 'amazon' toolkit is not SP-API
    "Salesforce Commerce Cloud": ["salesforcecommercecloud", "commercecloud"],
    "Google Ads ": ["googleads"], "Otter AI": ["otter", "otterai"],
    "Mermaid CLI": ["mermaid"], "YouTube Transcript": ["youtube"],
    "MongoDB Atlas": ["mongodb", "mongodbatlas"], "Bright Data": ["brightdata"],
    "GoHighLevel": ["gohighlevel", "highlevel"], "Paygent Connect": ["paygent"],
}


def fetch_catalog() -> set[str]:
    """Coarse fast-path membership set, pulled via the Composio SDK."""
    from composio import Composio
    c = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    slugs: set[str] = set()
    for t in c.toolkits.get():
        slug = getattr(t, "slug", None) or (t.get("slug") if isinstance(t, dict) else None)
        if slug:
            slugs.add(_norm(slug))
    return slugs


def _slug_exists(slug: str) -> bool:
    """Ground-truth per-slug check against Composio's API (catches catalog-page misses)."""
    import httpx
    try:
        r = httpx.get(f"https://backend.composio.dev/api/v3/toolkits/{slug}",
                      headers={"x-api-key": os.environ.get("COMPOSIO_API_KEY", "")}, timeout=15)
        return r.status_code == 200
    except Exception:
        return False


def main():
    slugs = fetch_catalog()
    print(f"Composio catalog: {len(slugs)} toolkits pulled via SDK (fast-path set)")

    run = json.loads((config.OUTPUT / "results.json").read_text(encoding="utf-8"))
    rows = run["apps"]

    checked, agree, mism = [], 0, []
    for a in rows:
        name = a["name"]
        # candidates: full name + name-without-parenthetical + explicit aliases
        # (deliberately NOT first-word, which caused "Zoho Cliq" -> "zoho" false positives)
        cands = {_norm(name), _norm(name.split("(")[0])}
        cands |= {_norm(x) for x in ALIASES.get(name, [])}
        cands = {x for x in cands if x}
        matched = next((x for x in cands if x in slugs), None)      # fast path (SDK set)
        if not matched:                                              # precise fallback
            matched = next((x for x in cands if _slug_exists(x)), None)
        in_catalog = matched is not None
        ours = a["fields"]["composio_toolkit"]["value"]   # yes / no / unknown
        composio_truth = "yes" if in_catalog else "no"
        row = {"id": a["id"], "name": name, "ours": ours, "composio": composio_truth,
               "matched_slug": matched}
        checked.append(row)
        # agreement only judged where we committed to yes/no
        if ours in ("yes", "no"):
            if ours == composio_truth:
                agree += 1
            else:
                mism.append(row)

    committed = [r for r in checked if r["ours"] in ("yes", "no")]
    acc = round(100 * agree / len(committed), 1) if committed else None
    report = {
        "catalog_size": len(slugs), "apps_checked": len(checked),
        "committed": len(committed), "agreements": agree,
        "agreement_pct": acc, "mismatches": mism,
    }
    (config.OUTPUT / "composio_catalog_check.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"composio_toolkit column agreement with live catalog: {acc}% "
          f"({agree}/{len(committed)} committed rows)")
    print(f"mismatches ({len(mism)}):")
    for m in mism:
        print(f"   {m['name']}: we said '{m['ours']}', catalog says '{m['composio']}'")
    print(f"-> {config.OUTPUT / 'composio_catalog_check.json'}")


if __name__ == "__main__":
    main()
