"""A deterministic local check-then-read race and one-file ordering control.

SQLite is a teaching fixture here, not an AWS or distributed design.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile


class ClosureRace:
    def __init__(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        self.split_data = root / "split-data.sqlite"
        self.split_authority = root / "split-authority.sqlite"
        self.joined = root / "joined.sqlite"
        for path in (self.split_data, self.joined):
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE notes (tenant TEXT PRIMARY KEY, body TEXT NOT NULL)")
                db.execute("INSERT INTO notes VALUES ('shop-a', 'private note')")
        for path in (self.split_authority, self.joined):
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE authority (tenant TEXT PRIMARY KEY, status TEXT NOT NULL)")
                db.execute("INSERT INTO authority VALUES ('shop-a', 'ACTIVE')")

    @staticmethod
    def _status(db: sqlite3.Connection) -> str:
        row = db.execute("SELECT status FROM authority WHERE tenant='shop-a'").fetchone()
        return row[0] if row else "UNKNOWN"

    @staticmethod
    def _note(db: sqlite3.Connection) -> str | None:
        row = db.execute("SELECT body FROM notes WHERE tenant='shop-a'").fetchone()
        return row[0] if row else None

    def split_read_with_closure_between(self) -> str:
        """Intentionally unsafe: close after an authority check, before data read."""
        with sqlite3.connect(self.split_authority) as authority:
            status = self._status(authority)
        if status != "ACTIVE":
            raise PermissionError("shop-a closed")
        with sqlite3.connect(self.split_authority) as authority:
            authority.execute("UPDATE authority SET status='CLOSED' WHERE tenant='shop-a'")
        with sqlite3.connect(self.split_data) as data:
            return self._note(data)

    def joined_read_with_close_attempt(self) -> tuple[str | None, bool]:
        """BEGIN IMMEDIATE serializes a local read with a competing close write."""
        with sqlite3.connect(self.joined, timeout=0) as reader:
            reader.execute("BEGIN IMMEDIATE")
            if self._status(reader) != "ACTIVE":
                raise PermissionError("shop-a closed")
            with sqlite3.connect(self.joined, timeout=0) as closer:
                try:
                    closer.execute("UPDATE authority SET status='CLOSED' WHERE tenant='shop-a'")
                except sqlite3.OperationalError as error:
                    if "locked" not in str(error).lower():
                        raise
                    close_blocked_until_read_finishes = True
                else:
                    close_blocked_until_read_finishes = False
            note = self._note(reader)
        return note, close_blocked_until_read_finishes

    def close_joined_after_read(self) -> None:
        with sqlite3.connect(self.joined) as db:
            db.execute("UPDATE authority SET status='CLOSED' WHERE tenant='shop-a'")

    def joined_read_after_close(self) -> str | None:
        with sqlite3.connect(self.joined) as db:
            db.execute("BEGIN IMMEDIATE")
            if self._status(db) != "ACTIVE":
                raise PermissionError("shop-a closed")
            return self._note(db)


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="amplify-tenant-race-") as folder:
        case = ClosureRace(Path(folder))
        unsafe_note = case.split_read_with_closure_between()
        joined_note, close_blocked = case.joined_read_with_close_attempt()
        case.close_joined_after_read()
        try:
            case.joined_read_after_close()
        except PermissionError:
            later_read_denied = True
        else:
            later_read_denied = False
        assert unsafe_note == joined_note == "private note"
        assert close_blocked and later_read_denied
        return {
            "split_check_then_close_then_read_leaks_note": True,
            "joined_close_blocked_during_read": close_blocked,
            "joined_read_before_close_succeeds": joined_note is not None,
            "joined_read_after_close_denied": later_read_denied,
            "scope": "one-host SQLite ordering; not distributed closure, cache or AWS proof",
        }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
