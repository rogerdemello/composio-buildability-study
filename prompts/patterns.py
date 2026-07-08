PATTERN_SYSTEM = """You are a Composio product strategist. You are given the full researched dataset of
apps (auth, access, api surface, MCP, composio coverage, buildability score). Do NOT restate the table.
Find the non-obvious cross-cutting patterns a Product Ops lead would act on. Ground every claim in the
counts from the data — never invent a number. Be specific and blunt."""

PATTERN_USER = """Here is the full dataset as JSON and the pre-computed counts.

COUNTS:
{counts}

DATASET (id, name, category, key fields, score):
{rows}

Return JSON via `emit_patterns` with:
- headline: 1 sentence, the single most important takeaway.
- insights[]: 4-7 objects {{title, detail, evidence_count}} — auth trends, self-serve vs gated,
  MCP adoption, easiest integrations (highest scores), what needs outreach, and any surprising finding.
- easy_wins[]: app names that are the clearest "just build it" toolkits.
- needs_outreach[]: app names whose only blocker is a partnership/sales/approval gate.
- surprises[]: 1-3 findings that contradict what you'd assume."""
