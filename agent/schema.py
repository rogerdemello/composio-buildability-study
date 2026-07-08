"""Shared schema + rubric for the app-research pipeline.

One record per app. The same JSON Schema is used to (a) force structured output
from the research agent and (b) validate every row before it lands in the dataset.
"""

from __future__ import annotations

# ---- Controlled vocabularies (kept small on purpose so patterns cluster cleanly) ----

AUTH_METHODS = ["OAuth2", "API Key", "Basic", "Token", "JWT", "PAT", "HMAC-signed", "Other", "None"]

ACCESS_MODELS = [
    "self-serve",       # free/trial account -> you generate creds yourself
    "sandbox-self-serve",  # sandbox/testnet creds self-serve & free; production is gated (common in fintech)
    "trial-only",       # only obtainable via a time-limited trial
    "gated-paid",       # needs a paid plan to unlock API access
    "gated-approval",   # app review / dev-token / production KYC you must pass
    "gated-partner",    # partnership / contact-sales gate
    "no-public-api",    # no documented public API at all
    "waitlist",         # API exists but access is waitlisted
]

API_SURFACES = ["REST", "GraphQL", "REST+GraphQL", "SDK-only", "gRPC", "SOAP", "CLI-tool", "none"]
API_BREADTH = ["broad", "moderate", "narrow", "n/a"]
MCP_STATUS = ["official", "community", "none", "unknown"]
COMPOSIO_TOOLKIT = ["yes", "no", "unknown"]
BUILDABILITY = ["easy", "moderate", "blocked"]
CONFIDENCE = ["high", "medium", "low"]

# ---- Rubric (shared with the agent prompt so humans and the model score the same way) ----

BUILDABILITY_RUBRIC = """
easy     = public, self-serve API (key or an OAuth app you create yourself),
           reasonably broad surface, credentials obtainable free/trial/sandbox.
moderate = public API but with friction: OAuth app review / dev-token approval,
           paid-plan-gated (but obtainable), narrow surface, or complex auth setup.
blocked  = no public API, partner / contact-sales / enterprise-only gate, or an
           approval a developer cannot self-obtain.
"""

# ---- JSON Schema used for tool-forced structured output + validation ----

RECORD_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "id", "name", "category", "one_liner", "auth_methods", "auth_note",
        "access", "access_note", "api_surface", "api_breadth", "has_mcp",
        "mcp_note", "composio_toolkit", "buildability", "main_blocker",
        "evidence_url", "confidence",
    ],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "category": {"type": "string"},
        "one_liner": {"type": "string", "description": "<=12 words, what it does"},
        "auth_methods": {"type": "array", "items": {"enum": AUTH_METHODS}, "minItems": 1},
        "auth_note": {"type": "string"},
        "access": {"enum": ACCESS_MODELS},
        "access_note": {"type": "string"},
        "api_surface": {"enum": API_SURFACES},
        "api_breadth": {"enum": API_BREADTH},
        "has_mcp": {"enum": MCP_STATUS},
        "mcp_note": {"type": "string"},
        "composio_toolkit": {"enum": COMPOSIO_TOOLKIT},
        "buildability": {"enum": BUILDABILITY},
        "main_blocker": {"type": "string", "description": "short, or 'none'"},
        "evidence_url": {"type": "string", "description": "canonical docs URL actually confirmed"},
        "confidence": {"enum": CONFIDENCE},
    },
}


def validate_record(rec: dict) -> list[str]:
    """Lightweight, dependency-free validation. Returns a list of problems (empty == ok)."""
    problems: list[str] = []
    for key in RECORD_SCHEMA["required"]:
        if key not in rec:
            problems.append(f"missing key: {key}")
    if not problems:
        if rec["access"] not in ACCESS_MODELS:
            problems.append(f"bad access: {rec['access']}")
        if rec["api_surface"] not in API_SURFACES:
            problems.append(f"bad api_surface: {rec['api_surface']}")
        if rec["buildability"] not in BUILDABILITY:
            problems.append(f"bad buildability: {rec['buildability']}")
        if rec["has_mcp"] not in MCP_STATUS:
            problems.append(f"bad has_mcp: {rec['has_mcp']}")
        if rec["confidence"] not in CONFIDENCE:
            problems.append(f"bad confidence: {rec['confidence']}")
        for m in rec.get("auth_methods", []):
            if m not in AUTH_METHODS:
                problems.append(f"bad auth_method: {m}")
        if not str(rec.get("evidence_url", "")).startswith("http"):
            problems.append("evidence_url is not a URL")
    return problems
