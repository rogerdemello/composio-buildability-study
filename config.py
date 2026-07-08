"""Central configuration. Everything overridable by env (.env)."""

import os
import pathlib

try:  # load .env if python-dotenv is installed (optional)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
WEB = ROOT / "web"
DATABASE = ROOT / "database"

# LLM backend: "nvidia" (NVIDIA NIM, OpenAI-compatible) by default, or "anthropic".
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "nvidia").lower()

# Sensible default models per provider (override any of them via env).
# Researcher uses a fast strong model; verifier/pattern use a larger, different one
# so the audit is genuinely a second opinion, not the same model re-reading itself.
_DEFAULTS = {
    "nvidia": {
        "research": "meta/llama-3.3-70b-instruct",
        "verify":   "meta/llama-3.1-405b-instruct",
        "pattern":  "meta/llama-3.1-405b-instruct",
    },
    "anthropic": {
        "research": "claude-sonnet-5",
        "verify":   "claude-opus-4-8",
        "pattern":  "claude-opus-4-8",
    },
}
_d = _DEFAULTS.get(LLM_PROVIDER, _DEFAULTS["nvidia"])
RESEARCH_MODEL = os.environ.get("RESEARCH_MODEL", _d["research"])
VERIFY_MODEL = os.environ.get("VERIFY_MODEL", _d["verify"])
PATTERN_MODEL = os.environ.get("PATTERN_MODEL", _d["pattern"])

CONCURRENCY = int(os.environ.get("CONCURRENCY", "5"))   # Semaphore width for parallel research
VERIFY_SAMPLE = int(os.environ.get("VERIFY_SAMPLE", "20"))

# Golden set: iterate the pipeline to perfection on these first (different auth models
# + categories), then scale. See README "How it was built".
GOLDEN = ["Salesforce", "HubSpot", "Slack", "Stripe", "Shopify"]

for d in (OUTPUT, DATA):
    d.mkdir(exist_ok=True)
