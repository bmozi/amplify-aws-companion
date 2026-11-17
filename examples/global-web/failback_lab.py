"""Two local SQLite stores illustrate write authority and failback receipts.

This is an application contract exercise, not an AWS replication emulator.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path


class Store:
    def __init__(self, path: Path, name: str):
        self.name = name
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE bookings (receipt TEXT PRIMARY KEY, slot TEXT UNIQUE, customer TEXT)")
        self.writer_open = False

    def book(self, receipt: str, slot: str, customer: str) -> str:
        if not self.writer_open:
            return "WRITE_CLOSED"
        try:
            self.db.execute("INSERT INTO bookings VALUES (?, ?, ?)", (receipt, slot, customer))
            self.db.commit()
        except sqlite3.IntegrityError:
            return "CONFLICT"
        return "ACCEPTED"

    def rows(self) -> list[tuple[str, str, str]]:
        return self.db.execute("SELECT receipt, slot, customer FROM bookings ORDER BY receipt").fetchall()

    def close(self) -> None:
        self.db.close()


def copy_and_check(source: Store, target: Store, acknowledged: set[str]) -> str:
    """Copy only while both toy writers are closed; check acknowledged rows exactly."""
    if source.writer_open or target.writer_open:
        return "NO_GO_WRITER_OPEN"
    source_rows = source.rows()
    if {row[0] for row in source_rows} != acknowledged:
        return "NO_GO_MISSING_SOURCE_RECEIPT"
    existing = target.rows()
    if any(row not in source_rows for row in existing):
        return "NO_GO_MISMATCH"
    try:
        with target.db:
            for row in source_rows:
                if row not in existing:
                    target.db.execute("INSERT INTO bookings VALUES (?, ?, ?)", row)
    except sqlite3.IntegrityError:
        return "NO_GO_CONFLICT"
    if target.rows() != source_rows:
        return "NO_GO_MISMATCH"
    return "READY"


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="a21-failback-") as folder:
        root = Path(folder)
        first = Store(root / "first.sqlite", "first")
        second = Store(root / "second.sqlite", "second")
        try:
            first.writer_open = True
            assert first.book("r-alice", "09:00", "Alice") == "ACCEPTED"
            first.writer_open = False
            forward = copy_and_check(first, second, {"r-alice"})
            assert forward == "READY"
            second.writer_open = True
            assert second.book("r-bob", "10:00", "Bob") == "ACCEPTED"

            # Traffic can point at the first store even while its copy is stale.
            stale_return = {"route": "first", "visible": [row[0] for row in first.rows()],
                            "missing_confirmed": [row[0] for row in second.rows()
                                                  if row[0] not in {item[0] for item in first.rows()}]}
            premature = copy_and_check(second, first, {"r-alice", "r-bob"})
            second.writer_open = False
            reverse = copy_and_check(second, first, {"r-alice", "r-bob"})
            assert reverse == "READY"
            first.writer_open = True
            safe_return = {"route": "first", "visible": [row[0] for row in first.rows()],
                           "old_writer_closed": not second.writer_open}
            return {"forward": forward, "stale_return": stale_return,
                    "premature_reverse": premature, "reverse": reverse,
                    "safe_return": safe_return}
        finally:
            first.close()
            second.close()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
