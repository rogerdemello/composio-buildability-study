"""Verifier agent: independent, adversarial re-check of the graded fields + evidence liveness.

Deliberately uses a *different, stronger* model and a fresh evidence gather so it is not
just re-reading the researcher's own conclusions. Returns per-field verdicts (PASS/FAIL/UNKNOWN)
that feed back into each Field's confidence and verifier state.
"""

from __future__ import annotations

import json

from models.app import AppResult, Verifier
from prompts import VERIFY_SYSTEM, VERIFY_USER
from providers.docs_fetcher import DocsFetcher

GRADED = ["auth_methods", "access", "api_surface", "has_mcp", "buildability"]

EMIT_VERDICTS = {
    "name": "emit_verdicts",
    "description": "Return an independent verdict per graded field.",
    "input_schema": {
        "type": "object", "additionalProperties": False, "required": ["verdicts"],
        "properties": {"verdicts": {"type": "object", "description": "field -> {verdict,value,confidence,why}"}},
    },
}


class VerifyAgent:
    def __init__(self, researcher, model="claude-opus-4-8", client=None):
        self.researcher = researcher            # reused for its evidence-gathering
        self.model = model
        if client is None:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic()
        self.client = client
        self.fetcher = DocsFetcher()

    async def verify(self, app_meta: dict, result: AppResult) -> AppResult:
        docs = await self.researcher._gather(app_meta)
        prior = {k: result.val(k) for k in GRADED}

        msg = await self.client.messages.create(
            model=self.model, max_tokens=1500, system=VERIFY_SYSTEM,
            tools=[EMIT_VERDICTS], tool_choice={"type": "tool", "name": "emit_verdicts"},
            messages=[{"role": "user", "content": VERIFY_USER.format(
                name=result.name, category=result.category,
                prior=json.dumps(prior, ensure_ascii=False),
                context=self.researcher._context(docs))}],
        )
        verdicts = next(b.input for b in msg.content
                        if getattr(b, "type", None) == "tool_use")["verdicts"]

        for k in GRADED:
            v = verdicts.get(k) or {}
            verdict = str(v.get("verdict", "unknown")).lower()
            f = result.fields.get(k)
            if not f:
                continue
            if verdict == "pass":
                f.verifier = Verifier.PASS
                f.confidence = min(0.99, max(f.confidence, 0.9))
            elif verdict == "fail":
                f.verifier = Verifier.FAIL          # flagged for human; value NOT auto-overwritten
                f.verifier_note = f"audit says: {v.get('value')} — {v.get('why','')}"
            else:
                f.verifier = Verifier.UNKNOWN

        # evidence liveness across this app's sources
        for k in GRADED:
            f = result.fields.get(k)
            if f and f.sources:
                live, status = await self.fetcher.is_live(f.sources[0].url)
                f.verifier_note += f" [evidence {status}{'' if live else ' DEAD'}]"
        return result
