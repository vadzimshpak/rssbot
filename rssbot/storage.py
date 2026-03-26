from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SqliteStorage:
    path: Path

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS posted_items (
                    item_id TEXT PRIMARY KEY,
                    posted_at TEXT NOT NULL
                )
                """.strip()
            )
            con.commit()

    def was_posted(self, item_id: str) -> bool:
        with self._connect() as con:
            cur = con.execute("SELECT 1 FROM posted_items WHERE item_id = ? LIMIT 1", (item_id,))
            return cur.fetchone() is not None

    def mark_posted(self, item_id: str, *, posted_at_iso: str) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO posted_items (item_id, posted_at) VALUES (?, ?)",
                (item_id, posted_at_iso),
            )
            con.commit()

    def filter_new(self, item_ids: Iterable[str]) -> list[str]:
        ids = [x for x in item_ids if x]
        if not ids:
            return []
        with self._connect() as con:
            q_marks = ",".join(["?"] * len(ids))
            cur = con.execute(
                f"SELECT item_id FROM posted_items WHERE item_id IN ({q_marks})",
                tuple(ids),
            )
            existing = {row[0] for row in cur.fetchall()}
        return [x for x in ids if x not in existing]

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.path))
        con.execute("PRAGMA journal_mode=WAL;")
        return con
