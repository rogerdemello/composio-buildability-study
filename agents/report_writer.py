"""Report writer: renders the self-contained case study from JSON.

No hand-written findings — every number and row comes from output/results.json,
output/patterns.json and data/verification_report.json. The HTML is CSP-safe
(all CSS/JS inlined, no CDN) because it is published as an Artifact.
"""

from __future__ import annotations

import json

import config


class ReportWriter:
    def __init__(self, repo_url: str = "https://github.com/rogerdemello/composio-buildability-study"):
        self.repo_url = repo_url

    def build(self) -> str:
        results = json.loads((config.OUTPUT / "results.json").read_text(encoding="utf-8"))
        patterns = json.loads((config.OUTPUT / "patterns.json").read_text(encoding="utf-8"))
        verify = json.loads((config.DATA / "verification_report.json").read_text(encoding="utf-8"))

        tpl = (config.WEB / "report_template.html").read_text(encoding="utf-8")
        tpl = tpl.replace("/*__RESULTS__*/{}", json.dumps(results, ensure_ascii=False))
        tpl = tpl.replace("/*__PATTERNS__*/{}", json.dumps(patterns, ensure_ascii=False))
        tpl = tpl.replace("/*__VERIFY__*/{}", json.dumps(verify, ensure_ascii=False))
        tpl = tpl.replace("__REPO_URL__", self.repo_url)

        out = config.WEB / "index.html"
        out.write_text(tpl, encoding="utf-8")

        # also publish to docs/ for GitHub Pages (public live link)
        docs = config.ROOT / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "index.html").write_text(tpl, encoding="utf-8")
        (docs / ".nojekyll").write_text("", encoding="utf-8")  # serve as-is, no Jekyll
        return str(out)
