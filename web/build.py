"""Inject the data into template.html -> index.html (self-contained, no external deps).

    python web/build.py [--repo <github-url>]
"""
import argparse, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB, DATA = ROOT / "web", ROOT / "data"

ap = argparse.ArgumentParser()
ap.add_argument("--repo", default="https://github.com/rogerdemello/composio-buildability-study")
args = ap.parse_args()

apps = json.loads((DATA / "apps.json").read_text(encoding="utf-8"))
verify = json.loads((DATA / "verification_report.json").read_text(encoding="utf-8"))

html = (WEB / "template.html").read_text(encoding="utf-8")
html = html.replace("/*__APPS__*/[]", json.dumps(apps, ensure_ascii=False))
html = html.replace("/*__VERIFY__*/{}", json.dumps(verify, ensure_ascii=False))
html = html.replace("__REPO_URL__", args.repo)

(WEB / "index.html").write_text(html, encoding="utf-8")
print(f"built web/index.html  ({len(html):,} bytes, {len(apps)} apps)")
