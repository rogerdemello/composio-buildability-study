"""Run-level container: the whole research run + its metadata + serialization."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from .app import AppResult


@dataclass
class RunMeta:
    generated_at: str = ""          # stamped by the caller (scripts can't call Date.now safely)
    model_research: str = "claude-sonnet-5"
    model_verify: str = "claude-opus-4-8"
    providers: list[str] = field(default_factory=list)
    n_apps: int = 0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class ResearchRun:
    apps: list[AppResult] = field(default_factory=list)
    meta: RunMeta = field(default_factory=RunMeta)

    def to_dict(self) -> dict:
        return {"meta": self.meta.to_dict(), "apps": [a.to_dict() for a in self.apps]}

    @staticmethod
    def from_dict(d: dict) -> "ResearchRun":
        r = ResearchRun()
        r.meta = RunMeta(**d.get("meta", {}))
        r.apps = [AppResult.from_dict(a) for a in d.get("apps", [])]
        return r
