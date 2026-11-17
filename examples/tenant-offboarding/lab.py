"""Local tenant offboarding boundary; synthetic identities and one SQLite store."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path


MEMBERS = {"alice": "shop-a", "bob": "shop-b"}
ADMINS = {"operator-a": "shop-a", "operator-b": "shop-b"}


class Portal:
    def __init__(self, path: Path):
        self.path = path
        self.cache: dict[tuple[str, str], str] = {}
        with sqlite3.connect(path) as db:
            db.executescript("""
                CREATE TABLE tenants (id TEXT PRIMARY KEY, status TEXT NOT NULL);
                CREATE TABLE notes (tenant TEXT, id TEXT, body TEXT,
                    PRIMARY KEY (tenant, id));
                CREATE TABLE jobs (id INTEGER PRIMARY KEY, tenant TEXT, note_id TEXT,
                    status TEXT NOT NULL);
                CREATE TABLE receipts (tenant TEXT PRIMARY KEY, body TEXT NOT NULL);
                INSERT INTO tenants VALUES ('shop-a', 'ACTIVE'), ('shop-b', 'ACTIVE');
                INSERT INTO notes VALUES
                    ('shop-a', 'same-id', 'Alice private note'),
                    ('shop-b', 'same-id', 'Bob private note');
            """)

    def _member(self, actor: str) -> str:
        tenant = MEMBERS.get(actor)
        if tenant is None:
            raise PermissionError("Unknown fixture member")
        return tenant

    @staticmethod
    def _require_active(db: sqlite3.Connection, tenant: str) -> None:
        row = db.execute("SELECT status FROM tenants WHERE id=?", (tenant,)).fetchone()
        if row != ("ACTIVE",):
            raise PermissionError("Tenant is not active")

    def read(self, actor: str, note_id: str) -> str:
        tenant = self._member(actor)
        with sqlite3.connect(self.path) as db:
            self._require_active(db, tenant)  # Check even when the cache is warm.
            key = (tenant, note_id)
            if key not in self.cache:
                row = db.execute(
                    "SELECT body FROM notes WHERE tenant=? AND id=?", key
                ).fetchone()
                if row is None:
                    raise PermissionError("Note unavailable")
                self.cache[key] = row[0]
            return self.cache[key]

    def enqueue(self, actor: str, note_id: str) -> int:
        tenant = self._member(actor)
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            self._require_active(db, tenant)
            if db.execute(
                "SELECT 1 FROM notes WHERE tenant=? AND id=?", (tenant, note_id)
            ).fetchone() is None:
                raise PermissionError("Note unavailable")
            return db.execute(
                "INSERT INTO jobs(tenant,note_id,status) VALUES (?,?, 'PENDING')",
                (tenant, note_id),
            ).lastrowid

    def process(self, job_id: int) -> str:
        """Return a local note; this fixture performs no external effect."""
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT tenant,note_id,status FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
            if row is None or row[2] != "PENDING":
                raise PermissionError("Job unavailable")
            tenant, note_id, _ = row
            self._require_active(db, tenant)
            note = db.execute(
                "SELECT body FROM notes WHERE tenant=? AND id=?", (tenant, note_id)
            ).fetchone()
            if note is None:
                raise PermissionError("Note unavailable")
            db.execute("UPDATE jobs SET status='DONE' WHERE id=?", (job_id,))
            return note[0]

    def offboard(self, operator: str, tenant: str) -> dict:
        if ADMINS.get(operator) != tenant:
            raise PermissionError("Operator is not assigned to this fixture tenant")
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT body FROM receipts WHERE tenant=?", (tenant,)
            ).fetchone()
            if prior is not None:
                return json.loads(prior[0])
            self._require_active(db, tenant)
            pending = db.execute(
                "SELECT count(*) FROM jobs WHERE tenant=? AND status='PENDING'", (tenant,)
            ).fetchone()[0]
            done = db.execute(
                "SELECT count(*) FROM jobs WHERE tenant=? AND status='DONE'", (tenant,)
            ).fetchone()[0]
            removed = db.execute(
                "SELECT count(*) FROM notes WHERE tenant=?", (tenant,)
            ).fetchone()[0]
            db.execute("UPDATE tenants SET status='CLOSED' WHERE id=?", (tenant,))
            db.execute(
                "UPDATE jobs SET status='CANCELLED' WHERE tenant=? AND status='PENDING'",
                (tenant,),
            )
            db.execute("DELETE FROM notes WHERE tenant=?", (tenant,))
            receipt = {
                "tenant": tenant,
                "status": "CLOSED",
                "active_notes_removed": removed,
                "pending_jobs_cancelled": pending,
                "already_completed_jobs_to_review": done,
                "outside_this_fixture": ["backups", "object files", "search indexes", "external effects"],
            }
            db.execute(
                "INSERT INTO receipts VALUES (?,?)", (tenant, json.dumps(receipt, sort_keys=True))
            )
        self.cache = {key: value for key, value in self.cache.items() if key[0] != tenant}
        return receipt


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="amplify-offboard-") as folder:
        portal = Portal(Path(folder) / "portal.sqlite")
        portal.read("alice", "same-id")
        portal.read("bob", "same-id")
        portal.enqueue("alice", "same-id")
        result = portal.offboard("operator-a", "shop-a")
        assert portal.read("bob", "same-id") == "Bob private note"
        print(json.dumps(result, indent=2))
