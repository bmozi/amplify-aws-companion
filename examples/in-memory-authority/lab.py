"""Contrast volatile acknowledgment, durable acknowledgment, and old snapshots locally."""

import sqlite3
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


class Journal:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS receipts (operation_id TEXT PRIMARY KEY, intent TEXT NOT NULL)"
        )
        self.db.commit()

    def close(self):
        self.db.close()

    def all(self):
        return dict(self.db.execute("SELECT operation_id, intent FROM receipts ORDER BY operation_id"))

    def record(self, operation_id: str, intent: str):
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO receipts (operation_id, intent) VALUES (?, ?)",
                (operation_id, intent),
            )
            saved = self.db.execute(
                "SELECT intent FROM receipts WHERE operation_id=?", (operation_id,)
            ).fetchone()
            if saved != (intent,):
                raise ValueError("same operation ID with changed intent")

    def count(self, operation_id: str):
        return self.db.execute(
            "SELECT count(*) FROM receipts WHERE operation_id=?", (operation_id,)
        ).fetchone()[0]


class Worker:
    def __init__(self, journal: Journal):
        self.journal = journal
        self.memory = journal.all()

    def acknowledge_after_record(self, operation_id: str, intent: str):
        self.journal.record(operation_id, intent)
        self.memory[operation_id] = intent
        return operation_id

    def acknowledge_before_record(self, operation_id: str, intent: str):
        # The deliberately unsafe schedule stops before the journal write.
        self.memory[operation_id] = intent
        return operation_id


def run():
    if sys.flags.optimize:
        raise SystemExit("Run without -O: assertions are the exercise checks")
    with TemporaryDirectory(prefix="in-memory-authority-") as directory:
        root = Path(directory)
        durable_path = root / "durable.sqlite"
        durable = Journal(durable_path)
        durable.record("R16", "confirm repair A")
        old_snapshot = durable.all()
        worker = Worker(durable)
        receipt = worker.acknowledge_after_record("R17", "confirm repair B")
        assert receipt == "R17" and durable.count("R17") == 1
        durable.close()

        # A new connection and worker start with no previous process memory.
        reopened = Journal(durable_path)
        recovered = Worker(reopened)
        assert recovered.memory["R17"] == "confirm repair B"
        assert "R17" not in old_snapshot
        assert recovered.acknowledge_after_record("R17", "confirm repair B") == "R17"
        assert reopened.count("R17") == 1
        try:
            recovered.acknowledge_after_record("R17", "confirm a different repair")
        except ValueError:
            pass
        else:
            raise AssertionError("changed intent under one receipt must be rejected")
        assert reopened.all()["R17"] == "confirm repair B"
        reopened.close()
        print("PASS: record-before-ack survives worker replacement; old snapshot alone omits R17")
        print("PASS: same-intent retry retains one receipt; changed intent is rejected")

        unsafe_path = root / "volatile.sqlite"
        unsafe = Journal(unsafe_path)
        unsafe.record("R16", "confirm repair A")
        volatile_worker = Worker(unsafe)
        unsafe_receipt = volatile_worker.acknowledge_before_record("R17", "confirm repair B")
        assert unsafe_receipt == "R17" and volatile_worker.memory["R17"] == "confirm repair B"
        assert unsafe.count("R17") == 0
        unsafe.close()
        reopened_unsafe = Journal(unsafe_path)
        after_loss = Worker(reopened_unsafe)
        assert "R17" not in after_loss.memory
        reopened_unsafe.close()
        print("PASS: ack-before-record loses R17 after volatile memory is discarded")

    assert not durable_path.exists() and not unsafe_path.exists()
    print("PASS: temporary journals removed; no AWS durability, timing, or cost claim")


if __name__ == "__main__":
    run()
