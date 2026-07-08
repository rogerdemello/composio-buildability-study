"""Central configuration. Everything overridable by env (.env)."""

import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
WEB = ROOT / "web"
DATABASE = ROOT / "database"

RESEARCH_MODEL = os.environ.get("RESEARCH_MODEL", "claude-sonnet-5")
VERIFY_MODEL = os.environ.get("VERIFY_MODEL", "claude-opus-4-8")
PATTERN_MODEL = os.environ.get("PATTERN_MODEL", "claude-opus-4-8")

CONCURRENCY = int(os.environ.get("CONCURRENCY", "5"))   # Semaphore width for parallel research
VERIFY_SAMPLE = int(os.environ.get("VERIFY_SAMPLE", "20"))

# Golden set: iterate the pipeline to perfection on these first (different auth models
# + categories), then scale. See README "How it was built".
GOLDEN = ["Salesforce", "HubSpot", "Slack", "Stripe", "Shopify"]

for d in (OUTPUT, DATA):
    d.mkdir(exist_ok=True)
