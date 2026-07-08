"""
Core data model.

The design decision that matters: confidence and provenance live **per field**,
not per app. "Salesforce is 90% confident" is useless; "Salesforce.auth is 0.98,
sourced from the OAuth docs, retrieved by docs_fetcher, verified PASS by the
verifier LLM, checked by a human" is what Product Ops actually needs.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---- controlled vocab (kept small so patterns cluster cleanly) --------------

AUTH_METHODS = ["OAuth2", "API Key", "Basic", "Token", "JWT", "PAT", "HMAC-signed", "Other", "None"]
ACCESS_MODELS = [
    "self-serve", "sandbox-self-serve", "trial-only",
    "gated-paid", "gated-approval", "gated-partner", "no-public-api", "waitlist",
]
API_SURFACES = ["REST", "GraphQL", "REST+GraphQL", "SDK-only", "gRPC", "SOAP", "CLI-tool", "none"]
API_BREADTH = ["broad", "moderate", "narrow", "n/a"]
MCP_STATUS = ["official", "community", "none", "unknown"]
COMPOSIO_TOOLKIT = ["yes", "no", "unknown"]
BUILDABILITY = ["easy", "moderate", "blocked"]


class Verifier(str, Enum):
    PASS = "pass"        # independent source agreed
    FAIL = "fail"        # independent source disagreed -> corrected
    UNKNOWN = "unknown"  # not independently verified


# ---- provenance primitives --------------------------------------------------

@dataclass
class Evidence:
    """One link in a field's provenance chain."""
    url: str
    retrieved_by: str = "docs_fetcher"   # tavily | firecrawl | docs_fetcher | browser | composio_search
    snippet: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class Field:
    """A single researched value carrying its own confidence + provenance."""
    value: Any
    confidence: float = 0.5              # 0..1
    sources: list[Evidence] = field(default_factory=list)
    verifier: Verifier = Verifier.UNKNOWN
    verifier_note: str = ""
    human_checked: bool = False

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "confidence": round(self.confidence, 2),
            "sources": [s.to_dict() for s in self.sources],
            "verifier": self.verifier.value if isinstance(self.verifier, Verifier) else self.verifier,
            "verifier_note": self.verifier_note,
            "human_checked": self.human_checked,
        }

    @staticmethod
    def from_dict(d: dict) -> "Field":
        return Field(
            value=d["value"],
            confidence=d.get("confidence", 0.5),
            sources=[Evidence(**s) for s in d.get("sources", [])],
            verifier=Verifier(d.get("verifier", "unknown")),
            verifier_note=d.get("verifier_note", ""),
            human_checked=d.get("human_checked", False),
        )


# ---- the app record ---------------------------------------------------------

RESEARCHED_FIELDS = [
    "one_liner", "auth_methods", "access", "api_surface", "api_breadth",
    "has_mcp", "composio_toolkit", "buildability", "main_blocker",
]


@dataclass
class AppResult:
    id: int
    name: str
    category: str
    fields: dict[str, Field] = field(default_factory=dict)
    buildability_score: int = 0
    score_breakdown: list[dict] = field(default_factory=list)

    # convenience accessors -------------------------------------------------
    def val(self, key: str) -> Any:
        f = self.fields.get(key)
        return f.value if f else None

    def app_confidence(self) -> float:
        """Rolls up field confidences (min is the honest headline number)."""
        vals = [f.confidence for f in self.fields.values()]
        return round(min(vals), 2) if vals else 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "category": self.category,
            "buildability_score": self.buildability_score,
            "score_breakdown": self.score_breakdown,
            "app_confidence": self.app_confidence(),
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
        }

    @staticmethod
    def from_dict(d: dict) -> "AppResult":
        a = AppResult(id=d["id"], name=d["name"], category=d["category"],
                      buildability_score=d.get("buildability_score", 0),
                      score_breakdown=d.get("score_breakdown", []))
        a.fields = {k: Field.from_dict(v) for k, v in d.get("fields", {}).items()}
        return a


# ---- buildability score -----------------------------------------------------
# A quantified 0..100 justification for the verdict, instead of a bare "easy".
# Each component is recorded so the UI can show *why* a score is what it is.

def score_buildability(app: AppResult) -> tuple[int, list[dict]]:
    """0..100 score. Access is the dominant lever (a great API you can't get creds
    for is not buildable), so gated apps are hard-capped into the lower bands."""
    breakdown: list[dict] = []

    def add(points: int, reason: str):
        if points:
            breakdown.append({"points": points, "reason": reason})

    add(8, "Base")

    auth = app.val("auth_methods") or []
    if not auth or "None" in auth:
        add(2, "No API auth required")
    else:
        add(8, f"Usable API auth ({', '.join(auth[:2])})")
        if "OAuth2" in auth:
            add(4, "OAuth2 supported")
        if any(a in auth for a in ("API Key", "Token", "PAT")):
            add(4, "Simple key/token path")

    surface = app.val("api_surface")
    if surface in ("REST", "GraphQL", "REST+GraphQL"):
        add(16, f"Documented {surface} API")
    elif surface in ("gRPC", "SOAP"):
        add(8, f"{surface} API")
    elif surface in ("SDK-only", "CLI-tool"):
        add(6, f"{surface} (callable, not plain HTTP)")
    elif surface == "none":
        add(-12, "No usable API surface")

    add({"broad": 10, "moderate": 5, "narrow": 2}.get(app.val("api_breadth"), 0),
        f"API breadth: {app.val('api_breadth')}")

    mcp = app.val("has_mcp")
    add({"official": 10, "community": 5}.get(mcp, 0),
        {"official": "Official MCP server", "community": "Community MCP server"}.get(mcp, "No MCP yet"))

    if app.val("composio_toolkit") == "yes":
        add(5, "Already a Composio toolkit (proven integrable)")

    access = app.val("access")
    add({
        "self-serve": 32, "sandbox-self-serve": 22, "trial-only": 8, "waitlist": 4,
        "gated-paid": -4, "gated-approval": -6, "gated-partner": -30, "no-public-api": -38,
    }.get(access, 0), f"Access: {access}")

    bf = app.fields.get("buildability")
    if bf and bf.confidence < 0.7:
        add(-10, "Thin/ambiguous docs (low confidence)")

    total = max(0, min(100, sum(b["points"] for b in breakdown)))

    # hard caps: gating you cannot self-clear dominates everything above it
    cap = {"gated-partner": 33, "no-public-api": 30, "gated-approval": 60, "gated-paid": 66}.get(access)
    if cap is not None and total > cap:
        breakdown.append({"points": cap - total, "reason": f"Cap: {access} can't be self-cleared"})
        total = cap
    return total, breakdown


def _norm_auth(v) -> list[str]:
    out = []
    for x in (v if isinstance(v, list) else [v]):
        s = str(x).lower()
        if "oauth" in s: out.append("OAuth2")
        elif "jwt" in s: out.append("JWT")
        elif "hmac" in s: out.append("HMAC-signed")
        elif "pat" in s or "personal access" in s: out.append("PAT")
        elif "api key" in s or "apikey" in s or "api-key" in s: out.append("API Key")
        elif "token" in s: out.append("Token")
        elif "basic" in s: out.append("Basic")
        elif "key" in s: out.append("API Key")
        elif "none" in s or s in ("", "n/a"): out.append("None")
        else: out.append("Other")
    seen = []
    for a in out:
        if a not in seen: seen.append(a)
    return seen or ["Other"]


def _norm_access(v) -> str:
    s = str(v).lower()
    if "no public" in s or "no-public" in s or "no api" in s: return "no-public-api"
    if "waitlist" in s: return "waitlist"
    if "sandbox" in s or "testnet" in s: return "sandbox-self-serve"
    if "partner" in s or "contact" in s or "enterprise" in s or "sales" in s: return "gated-partner"
    if "approval" in s or "review" in s or "kyc" in s or "verif" in s or "dev token" in s: return "gated-approval"
    if "trial" in s: return "trial-only"
    if "paid" in s or "subscription" in s: return "gated-paid"
    if "self" in s or "public" in s or "free" in s: return "self-serve"
    return "self-serve"


def _norm_surface(v) -> str:
    s = str(v).lower()
    r, g = "rest" in s, "graphql" in s
    if r and g: return "REST+GraphQL"
    if g: return "GraphQL"
    if r: return "REST"
    if "grpc" in s: return "gRPC"
    if "soap" in s: return "SOAP"
    if "cli" in s: return "CLI-tool"
    if "sdk" in s: return "SDK-only"
    if "none" in s or "no api" in s: return "none"
    return "REST"


def _pick(v, allowed, default):
    s = str(v).lower().strip()
    for a in allowed:
        if a.lower() in s:
            return a
    return default


def normalize_record(rec: dict) -> dict:
    """Map an LLM's free-text field values onto the controlled vocab.

    Different providers (NVIDIA NIM, Anthropic, …) phrase enums differently
    ("OAuth 2.0" vs "OAuth2", "public self-serve API" vs "self-serve"); this keeps
    the dataset clean and the score correct regardless of which model produced it.
    """
    def val(k):
        c = rec.get(k)
        return c.get("value") if isinstance(c, dict) else c

    def setv(k, v):
        if isinstance(rec.get(k), dict): rec[k]["value"] = v
        else: rec[k] = v

    if "auth_methods" in rec: setv("auth_methods", _norm_auth(val("auth_methods")))
    if "access" in rec: setv("access", _norm_access(val("access")))
    if "api_surface" in rec: setv("api_surface", _norm_surface(val("api_surface")))
    if "api_breadth" in rec: setv("api_breadth", _pick(val("api_breadth"), API_BREADTH, "moderate"))
    if "has_mcp" in rec: setv("has_mcp", _pick(val("has_mcp"), MCP_STATUS, "unknown"))
    if "composio_toolkit" in rec: setv("composio_toolkit", _pick(val("composio_toolkit"), COMPOSIO_TOOLKIT, "unknown"))
    return rec


def verdict_from_score(score: int) -> str:
    if score >= 68:
        return "easy"
    if score >= 34:
        return "moderate"
    return "blocked"
