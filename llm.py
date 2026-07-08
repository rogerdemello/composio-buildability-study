"""
Provider-agnostic LLM client.

All three agents need the same primitive: "given a system + user prompt and a tool
schema, force a single structured tool call and return its parsed arguments." This
wraps that for two backends selected by env `LLM_PROVIDER`:

  - "nvidia"    -> NVIDIA NIM (OpenAI-compatible; build.nvidia.com)  [default]
  - "anthropic" -> Anthropic Claude

Switch providers with one env var; no agent code changes.
"""

from __future__ import annotations

import json
import os
import re

_JSON = re.compile(r"\{.*\}", re.S)


def _extract_json(text: str) -> dict:
    """Fallback when a model returns JSON in content instead of a tool call."""
    m = _JSON.search(text or "")
    return json.loads(m.group(0)) if m else {}


class LLM:
    def __init__(self, model: str, provider: str | None = None):
        self.provider = (provider or os.environ.get("LLM_PROVIDER", "nvidia")).lower()
        self.model = model
        self._client = None

    def _client_lazy(self):
        if self._client is not None:
            return self._client
        if self.provider == "anthropic":
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic()
        else:  # nvidia / any OpenAI-compatible endpoint
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
                api_key=os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY", ""),
            )
        return self._client

    async def structured(self, *, system: str, user: str, tool_name: str,
                         tool_desc: str, schema: dict, max_tokens: int = 2048) -> dict:
        """Force one tool/function call and return its arguments as a dict."""
        client = self._client_lazy()

        if self.provider == "anthropic":
            resp = await client.messages.create(
                model=self.model, max_tokens=max_tokens, system=system,
                tools=[{"name": tool_name, "description": tool_desc, "input_schema": schema}],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[{"role": "user", "content": user}],
            )
            for b in resp.content:
                if getattr(b, "type", None) == "tool_use":
                    return b.input
            raise RuntimeError("no tool_use block in Anthropic response")

        # OpenAI-compatible (NVIDIA NIM)
        resp = await client.chat.completions.create(
            model=self.model, max_tokens=max_tokens, temperature=0.2,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            tools=[{"type": "function", "function": {
                "name": tool_name, "description": tool_desc, "parameters": schema}}],
            tool_choice={"type": "function", "function": {"name": tool_name}},
        )
        msg = resp.choices[0].message
        if getattr(msg, "tool_calls", None):
            return json.loads(msg.tool_calls[0].function.arguments)
        return _extract_json(msg.content or "{}")   # graceful fallback for models that inline JSON
