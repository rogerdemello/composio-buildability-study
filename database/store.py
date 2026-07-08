"""Tiny JSON-file store. Idempotent by app id, so a crashed run resumes without
re-researching what's already done. (Swap for SQLite/Postgres behind this interface
if the set grows past a few thousand apps.)"""

from __future__ import annotations

import json
import pathlib

from models.app import AppResult
from models.result import ResearchRun, RunMeta


class Store:
    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)
        self.run = ResearchRun(meta=RunMeta())
        if self.path.exists():
            self.run = ResearchRun.from_dict(json.loads(self.path.read_text(encoding="utf-8")))
        self._by_id = {a.id: a for a in self.run.apps}

    def has(self, app_id: int) -> bool:
        return app_id in self._by_id

    def get(self, app_id: int) -> AppResult | None:
        return self._by_id.get(app_id)

    def upsert(self, app: AppResult) -> None:
        self._by_id[app.id] = app
        self.run.apps = [self._by_id[k] for k in sorted(self._by_id)]

    def save(self) -> None:
        self.run.meta.n_apps = len(self.run.apps)
        self.path.write_text(json.dumps(self.run.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
