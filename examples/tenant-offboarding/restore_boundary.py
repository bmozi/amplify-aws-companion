"""Show how an old app snapshot can resurrect a closed tenant's rows.

Sequential, local SQLite fixture only. It does not model distributed races.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3
import tempfile


class RestoreBoundary:
    def __init__(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        self.app = root / "app.sqlite"
        self.control = root / "closure.sqlite"
        self.old_app = root / "before-close-app.sqlite"
        self.old_control = root / "before-close-control.sqlite"
        with sqlite3.connect(self.app) as db:
            db.executescript("""
                CREATE TABLE notes (tenant TEXT, id TEXT, body TEXT,
                    PRIMARY KEY (tenant, id));
                CREATE TABLE jobs (tenant TEXT, id TEXT, status TEXT,
                    PRIMARY KEY (tenant, id));
                INSERT INTO notes VALUES
                    ('shop-a', 'same-id', 'Alice private note'),
                    ('shop-b', 'same-id', 'Bob private note');
                INSERT INTO jobs VALUES
                    ('shop-a', 'send-1', 'PENDING'),
                    ('shop-b', 'send-1', 'PENDING');
            """)
        with sqlite3.connect(self.control) as db:
            db.executescript("""
                CREATE TABLE closure (tenant TEXT PRIMARY KEY, status TEXT NOT NULL);
                INSERT INTO closure VALUES ('shop-a', 'ACTIVE'), ('shop-b', 'ACTIVE');
            """)
        shutil.copy2(self.app, self.old_app)
        shutil.copy2(self.control, self.old_control)
        with sqlite3.connect(self.app) as db:
            db.execute("UPDATE notes SET body='Bob newer note' WHERE tenant='shop-b' AND id='same-id'")

    def close_shop_a(self) -> None:
        # The two files do not share an atomic transaction. A real design needs
        # a durable, authoritative ordering and a reconciliation procedure.
        with sqlite3.connect(self.control) as db:
            db.execute("UPDATE closure SET status='CLOSED' WHERE tenant='shop-a'")
        with sqlite3.connect(self.app) as db:
            db.execute("DELETE FROM notes WHERE tenant='shop-a'")
            db.execute("UPDATE jobs SET status='CANCELLED' WHERE tenant='shop-a' AND status='PENDING'")

    def restore_old_app(self) -> None:
        shutil.copy2(self.old_app, self.app)

    def restore_old_control_too(self) -> None:
        """Intentional negative control: erases the newer closure decision."""
        shutil.copy2(self.old_control, self.control)

    def raw_note(self, tenant: str) -> str | None:
        with sqlite3.connect(self.app) as db:
            row = db.execute("SELECT body FROM notes WHERE tenant=? AND id='same-id'", (tenant,)).fetchone()
            return row[0] if row else None

    def _require_active(self, tenant: str) -> None:
        try:
            if not self.control.is_file():
                raise sqlite3.OperationalError("closure ledger unavailable")
            with sqlite3.connect(f"file:{self.control}?mode=ro", uri=True) as db:
                row = db.execute("SELECT status FROM closure WHERE tenant=?", (tenant,)).fetchone()
            if row != ("ACTIVE",):
                raise PermissionError("tenant closed or unknown")
        except sqlite3.Error as error:
            raise PermissionError("closure authority unavailable") from error

    def read(self, tenant: str) -> str | None:
        self._require_active(tenant)
        return self.raw_note(tenant)

    def pending_job(self, tenant: str) -> str | None:
        self._require_active(tenant)
        with sqlite3.connect(self.app) as db:
            row = db.execute("SELECT status FROM jobs WHERE tenant=? AND id='send-1'", (tenant,)).fetchone()
            return row[0] if row else None

    def reconcile_closed_shop_a(self) -> dict[str, int]:
        try:
            if not self.control.is_file():
                raise sqlite3.OperationalError("closure ledger unavailable")
            with sqlite3.connect(f"file:{self.control}?mode=ro", uri=True) as authority:
                status = authority.execute("SELECT status FROM closure WHERE tenant='shop-a'").fetchone()
        except sqlite3.Error as error:
            raise PermissionError("closure authority unavailable") from error
        if status != ("CLOSED",):
            raise PermissionError("shop-a has no closure decision")
        with sqlite3.connect(self.app) as db:
            db.execute("BEGIN IMMEDIATE")
            notes = db.execute("SELECT count(*) FROM notes WHERE tenant='shop-a'").fetchone()[0]
            jobs = db.execute("SELECT count(*) FROM jobs WHERE tenant='shop-a' AND status='PENDING'").fetchone()[0]
            db.execute("DELETE FROM notes WHERE tenant='shop-a'")
            db.execute("UPDATE jobs SET status='CANCELLED' WHERE tenant='shop-a' AND status='PENDING'")
        return {"restored_notes_removed": notes, "restored_jobs_cancelled": jobs}


def demonstrate() -> dict:
    with tempfile.TemporaryDirectory(prefix="amplify-tenant-restore-") as folder:
        case = RestoreBoundary(Path(folder))
        case.close_shop_a()
        case.restore_old_app()
        raw_resurrection = case.raw_note("shop-a") == "Alice private note"
        try:
            case.read("shop-a")
        except PermissionError:
            guarded_read_denied = True
        else:
            guarded_read_denied = False
        try:
            case.pending_job("shop-a")
        except PermissionError:
            guarded_job_denied = True
        else:
            guarded_job_denied = False
        other_tenant_works = case.read("shop-b") == "Bob private note"
        other_tenant_newer_value_lost = other_tenant_works
        reconciliation = case.reconcile_closed_shop_a()
        assert raw_resurrection and guarded_read_denied and guarded_job_denied and other_tenant_works
        assert reconciliation == {"restored_notes_removed": 1, "restored_jobs_cancelled": 1}
        assert case.raw_note("shop-a") is None
        return {
            "raw_old_snapshot_contains_closed_tenant": raw_resurrection,
            "guarded_read_denied": guarded_read_denied,
            "guarded_job_denied": guarded_job_denied,
            "other_tenant_available": other_tenant_works,
            "other_tenant_newer_value_lost": other_tenant_newer_value_lost,
            "reconciliation": reconciliation,
            "scope": "sequential local SQLite fixture; no physical erase or AWS restore proof",
        }


if __name__ == "__main__":
    print(json.dumps(demonstrate(), indent=2))
