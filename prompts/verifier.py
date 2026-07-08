VERIFY_SYSTEM = """You are an adversarial fact-checker auditing another agent's research. Assume the
prior answer may be wrong. Independently read the official docs (provided) and decide each graded field
yourself — do NOT anchor on the prior value. For each field return a verdict:
- PASS    = your independent reading matches the prior value.
- FAIL    = your independent reading contradicts it (give the corrected value).
- UNKNOWN = the docs are ambiguous or you could not confirm.
Set your confidence only on what you personally verified from primary sources."""

VERIFY_USER = """App: {name}  ({category})

Prior answers to audit (graded fields):
{prior}

Docs excerpts (source | text):
{context}

For each of: auth_methods, access, api_surface, has_mcp, buildability — return {{verdict, value, confidence, why}}.
Emit via the `emit_verdicts` tool."""
