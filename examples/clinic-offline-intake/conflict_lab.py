"""Cloud-free, single-SQLite model of stale offline closure and lost replies.

Fixture actor names are untrusted strings. This is not an AWS sync implementation.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path


class WorkOrder:
    def __init__(self, path: Path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS machine (
                machine_id TEXT PRIMARY KEY, revision INTEGER NOT NULL,
                status TEXT NOT NULL, last_report TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS operation (
                operation_id TEXT PRIMARY KEY, kind TEXT NOT NULL,
                payload TEXT NOT NULL, result TEXT NOT NULL
            )""")

    def read(self, machine_id: str) -> dict:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT revision,status,last_report FROM machine WHERE machine_id=?",
                (machine_id,),
            ).fetchone()
        if row is None:
            raise KeyError(machine_id)
        return {"machine_id": machine_id, "revision": row[0],
                "status": row[1], "last_report": row[2]}

    def apply(self, operation_id: str, kind: str, machine_id: str,
              expected_revision: int, report: str) -> dict:
        if not all(isinstance(x, str) and x for x in (operation_id, kind, machine_id, report)):
            raise ValueError("nonempty operation, kind, machine and report required")
        if kind not in {"report", "close"} or not isinstance(expected_revision, int) or expected_revision < 0:
            raise ValueError("kind must be report or close; expected revision must be nonnegative")
        payload = json.dumps([kind, machine_id, expected_revision, report], separators=(",", ":"))
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(
                "SELECT payload,result FROM operation WHERE operation_id=?", (operation_id,)
            ).fetchone()
            if old:
                if old[0] != payload:
                    raise ValueError("same operation ID with changed intent")
                return json.loads(old[1])

            row = db.execute(
                "SELECT revision,status,last_report FROM machine WHERE machine_id=?",
                (machine_id,),
            ).fetchone()
            current = row[0] if row else 0
            if expected_revision != current:
                result = {"decision": "STALE_REVIEW", "machine_id": machine_id,
                          "current_revision": current}
            elif kind == "close" and (row is None or row[1] != "open"):
                result = {"decision": "NOT_OPEN", "machine_id": machine_id,
                          "current_revision": current}
            else:
                revision = current + 1
                status = "open" if kind == "report" else "closed"
                if row is None:
                    db.execute("INSERT INTO machine VALUES (?,?,?,?)",
                               (machine_id, revision, status, report))
                else:
                    db.execute("UPDATE machine SET revision=?,status=?,last_report=? WHERE machine_id=?",
                               (revision, status, report, machine_id))
                result = {"decision": "APPLIED", "machine_id": machine_id,
                          "revision": revision, "status": status}
            db.execute("INSERT INTO operation VALUES (?,?,?,?)",
                       (operation_id, kind, payload, json.dumps(result, sort_keys=True)))
            return result


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="clinic-conflict-") as temp:
        path = Path(temp) / "authority.sqlite"
        server = WorkOrder(path)
        first = server.apply("open-1", "report", "pump-7", 0, "seal leak")
        old_device_revision = first["revision"]
        second = server.apply("hazard-2", "report", "pump-7", 1, "new electrical hazard")
        stale_close = server.apply("close-3", "close", "pump-7", old_device_revision,
                                   "older device says repaired")
        server = WorkOrder(path)  # server process replacement, same local file
        replay = server.apply("hazard-2", "report", "pump-7", 1, "new electrical hazard")
        current = server.read("pump-7")
        return {"first_report": first, "new_hazard": second,
                "stale_close": stale_close, "lost_reply_replay": replay,
                "current": current,
                "boundary": "One local SQLite writer authority; no trusted actor, real clock, offline device, AWS sync or human repair verification."}


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
