"""Local tenant-scoped message boundary. No SQS or authentication service is used."""

import json
import sqlite3
from pathlib import Path


MEMBERSHIPS = {"alice": "shop-a", "bob": "shop-b"}  # Public fixture identities.


class MessageBoundary:
    def __init__(self, path: Path):
        self.path = path
        with sqlite3.connect(path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS requests (
                    tenant TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    report TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (tenant, request_id)
                );
                CREATE TABLE IF NOT EXISTS effects (
                    tenant TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    report TEXT NOT NULL,
                    PRIMARY KEY (tenant, request_id)
                );
            """)

    def submit(self, actor: str, request_id: str, report: str,
               claimed_tenant: str | None = None) -> dict[str, str]:
        tenant = MEMBERSHIPS.get(actor)
        if tenant is None or (claimed_tenant is not None and claimed_tenant != tenant):
            raise PermissionError("Membership does not authorize this tenant")
        if not request_id or not report:
            raise ValueError("A stable request ID and report name are required")
        with sqlite3.connect(self.path) as db:
            old = db.execute("SELECT report FROM requests WHERE tenant=? AND request_id=?",
                             (tenant, request_id)).fetchone()
            if old is None:
                db.execute("INSERT INTO requests(tenant,request_id,report) VALUES(?,?,?)",
                           (tenant, request_id, report))
            elif old[0] != report:
                raise ValueError("Request ID already names a different report")
        # This resembles an SQS send envelope. It is not a signed claim or a send.
        return {"MessageGroupId": tenant, "tenant": tenant, "request_id": request_id}

    def pending_envelopes(self) -> list[dict[str, str]]:
        """Recover accepted work after a lost send; resending may cause duplicates."""
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT tenant,request_id FROM requests WHERE completed=0 "
                              "ORDER BY tenant,request_id").fetchall()
        return [{"MessageGroupId": tenant, "tenant": tenant, "request_id": request_id}
                for tenant, request_id in rows]

    def consume(self, envelope: dict[str, str]) -> str:
        tenant = envelope.get("tenant")
        request_id = envelope.get("request_id")
        if not tenant or not request_id or envelope.get("MessageGroupId") != tenant:
            raise PermissionError("Untrusted or inconsistent message route")
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT report,completed FROM requests WHERE tenant=? AND request_id=?",
                             (tenant, request_id)).fetchone()
            if row is None:
                raise PermissionError("No accepted request for this tenant")
            report, completed = row
            if not completed:
                db.execute("INSERT INTO effects(tenant,request_id,report) VALUES(?,?,?)",
                           (tenant, request_id, report))
                db.execute("UPDATE requests SET completed=1 WHERE tenant=? AND request_id=?",
                           (tenant, request_id))
            return report

    def effects(self) -> list[tuple[str, str, str]]:
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT tenant,request_id,report FROM effects ORDER BY tenant,request_id").fetchall()


if __name__ == "__main__":
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="tenant-message-boundary-") as temp:
        boundary = MessageBoundary(Path(temp) / "local.sqlite")
        a = boundary.submit("alice", "same-id", "A report")
        b = boundary.submit("bob", "same-id", "B report")
        boundary.consume(b)
        boundary.consume(a)
        boundary.consume(a)  # Duplicate delivery does not duplicate this local effect.
        print(json.dumps({"envelopes": [a, b], "local_effects": boundary.effects(),
                          "scope": "Synthetic memberships, SQLite transaction and internal consumer only; no SQS, distributed outbox, external effect or AWS cost evidence"}, indent=2))
