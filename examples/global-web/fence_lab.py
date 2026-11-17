"""Local stale-writer exercise. One SQLite authority, not a regional fence."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

from failback_lab import Store


class Authority:
    """Keep the epoch check and booking effect in one SQLite transaction."""

    def __init__(self, path: Path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE authority (id INTEGER PRIMARY KEY CHECK (id = 1), epoch INTEGER NOT NULL, owner TEXT NOT NULL)")
        self.db.execute("INSERT INTO authority VALUES (1, 1, 'first')")
        self.db.execute("CREATE TABLE bookings (receipt TEXT PRIMARY KEY, slot TEXT UNIQUE, customer TEXT)")
        self.db.commit()

    def current(self) -> tuple[int, str]:
        return self.db.execute("SELECT epoch, owner FROM authority WHERE id = 1").fetchone()

    def transfer(self, expected_epoch: int, expected_owner: str, next_owner: str) -> str:
        if expected_owner not in {"first", "second"} or next_owner not in {"first", "second"} or expected_owner == next_owner:
            return "INVALID_OWNER"
        with self.db:
            changed = self.db.execute(
                "UPDATE authority SET epoch = epoch + 1, owner = ? WHERE id = 1 AND epoch = ? AND owner = ?",
                (next_owner, expected_epoch, expected_owner),
            ).rowcount
        return "TRANSFERRED" if changed == 1 else "STALE_TRANSFER"

    def book(self, epoch: int, owner: str, receipt: str, slot: str, customer: str) -> str:
        # BEGIN IMMEDIATE serializes the authority decision with the write.
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if self.current() != (epoch, owner):
                self.db.rollback()
                return "STALE_WRITER"
            try:
                self.db.execute("INSERT INTO bookings VALUES (?, ?, ?)", (receipt, slot, customer))
            except sqlite3.IntegrityError:
                self.db.rollback()
                return "CONFLICT"
            self.db.commit()
            return "ACCEPTED"
        except Exception:
            self.db.rollback()
            raise

    def rows(self) -> list[tuple[str, str, str]]:
        return self.db.execute("SELECT receipt, slot, customer FROM bookings ORDER BY receipt").fetchall()

    def close(self) -> None:
        self.db.close()


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="a21-fence-") as folder:
        root = Path(folder)
        first = Store(root / "first.sqlite", "first")
        second = Store(root / "second.sqlite", "second")
        authority = Authority(root / "authority.sqlite")
        try:
            # Flags held separately by deployments can disagree after a move.
            first.writer_open = True
            second.writer_open = True
            flag_only = {
                "old_writer_after_move": first.book("r-old", "09:00", "Alice"),
                "new_writer_after_move": second.book("r-new", "09:00", "Bob"),
            }

            # A check *before* a separate write is not a guard on that write.
            old_precheck = authority.current() == (1, "first")
            moved = authority.transfer(1, "first", "second")
            old_after_precheck = first.book("r-late", "10:00", "Alice")
            precheck_only = {"old_precheck": old_precheck, "move": moved,
                             "old_write_after_move": old_after_precheck}

            # Here the token check and booking share one authoritative transaction.
            guarded = {
                "old_token_after_move": authority.book(1, "first", "r-old", "09:00", "Alice"),
                "new_token": authority.book(2, "second", "r-new", "09:00", "Bob"),
                "old_token_other_slot": authority.book(1, "first", "r-late", "10:00", "Alice"),
                "visible_receipts": [row[0] for row in authority.rows()],
            }
            return {"flag_only": flag_only, "precheck_only": precheck_only,
                    "atomic_local_authority": guarded}
        finally:
            first.close()
            second.close()
            authority.close()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
