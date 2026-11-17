"""Two local SQLite files rehearse durable export approval and a supplier copy.

This is an application contract fixture, not S3, KMS, IAM or cross-account AWS.
"""

from hashlib import sha256
from pathlib import Path
import sqlite3
import tempfile

from local_lab import ExportDenied, ExportLedger


class LostReply(RuntimeError):
    """A fixture operation committed, but its caller did not receive the reply."""


class OwnerLedger:
    def __init__(self, path: Path, approval_owner="Maya"):
        self.path = Path(path)
        self.approval_owner = approval_owner
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS exports (
                key TEXT NOT NULL, version TEXT NOT NULL, payload BLOB NOT NULL,
                digest TEXT NOT NULL, supplier TEXT, withdrawn INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (key, version))""")

    def stage(self, key, version, rows):
        # Reuse the first exercise's exact schema and canonical-byte rule.
        candidate = ExportLedger(self.approval_owner).stage(key, version, rows)
        try:
            with sqlite3.connect(self.path) as db:
                db.execute("INSERT INTO exports(key, version, payload, digest) VALUES (?, ?, ?, ?)",
                           (key, version, candidate.payload, candidate.digest))
        except sqlite3.IntegrityError as error:
            raise ExportDenied("a version label cannot be reused") from error
        return candidate

    def approve(self, key, version, digest, supplier, actor, *, lose_reply=False):
        if actor != self.approval_owner or not supplier:
            raise ExportDenied("approval needs the fixture owner and a supplier")
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT digest, supplier, withdrawn FROM exports WHERE key=? AND version=?",
                             (key, version)).fetchone()
            if row is None or row[0] != digest or row[2]:
                raise ExportDenied("approval must bind an existing, current exact version")
            if row[1] is not None and row[1] != supplier:
                raise ExportDenied("an approval cannot be reassigned")
            if row[1] is None:
                db.execute("UPDATE exports SET supplier=? WHERE key=? AND version=? AND supplier IS NULL",
                           (supplier, key, version))
                result = "approved"
            else:
                result = "already_approved"
        if lose_reply:
            raise LostReply("owner committed approval before reply was lost")
        return {"result": result, "key": key, "version": version, "digest": digest,
                "supplier": supplier}

    def approved_bytes(self, key, version, supplier):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT payload, digest, supplier, withdrawn FROM exports WHERE key=? AND version=?",
                             (key, version)).fetchone()
        if row is None or row[2] != supplier or row[3]:
            raise ExportDenied("no current grant for this supplier and exact version")
        if sha256(row[0]).hexdigest() != row[1]:
            raise ExportDenied("stored bytes do not match the approved digest")
        return row[0], row[1]

    def withdraw(self, key, version, actor):
        if actor != self.approval_owner:
            raise ExportDenied("only the fixture owner may withdraw")
        with sqlite3.connect(self.path) as db:
            changed = db.execute("UPDATE exports SET withdrawn=1 WHERE key=? AND version=?",
                                 (key, version)).rowcount
            if changed != 1:
                raise ExportDenied("unknown export version")


class SupplierShelf:
    def __init__(self, path: Path):
        self.path = Path(path)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS copies (
                key TEXT NOT NULL, version TEXT NOT NULL, supplier TEXT NOT NULL,
                payload BLOB NOT NULL, digest TEXT NOT NULL,
                PRIMARY KEY (key, version, supplier))""")

    def accept(self, owner: OwnerLedger, key, version, supplier, *, lose_reply=False,
               after_owner_read=None):
        payload, digest = owner.approved_bytes(key, version, supplier)
        if after_owner_read is not None:
            after_owner_read()
        return self.accept_bytes(key, version, supplier, payload, digest, lose_reply=lose_reply)

    def accept_bytes(self, key, version, supplier, payload, digest, *, lose_reply=False):
        """Persist bytes already delivered over an independently checked path.

        The caller is responsible for authenticating the delivery source; this
        shelf only checks exact bytes and repeated-copy consistency.
        """
        if sha256(payload).hexdigest() != digest:
            raise ExportDenied("received bytes do not match the claimed digest")
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR IGNORE INTO copies VALUES (?, ?, ?, ?, ?)",
                       (key, version, supplier, payload, digest))
            stored = db.execute("SELECT payload, digest FROM copies WHERE key=? AND version=? AND supplier=?",
                                (key, version, supplier)).fetchone()
            if stored != (payload, digest):
                raise ExportDenied("supplier shelf has conflicting bytes for this version")
        if lose_reply:
            raise LostReply("supplier committed copy before reply was lost")
        return {"key": key, "version": version, "supplier": supplier, "digest": digest}

    def lookup(self, key, version, supplier):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT payload, digest FROM copies WHERE key=? AND version=? AND supplier=?",
                             (key, version, supplier)).fetchone()
        if row is None or sha256(row[0]).hexdigest() != row[1]:
            raise ExportDenied("no verified supplier-held copy")
        return row


def run_demo():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        owner, shelf = OwnerLedger(root / "owner.sqlite"), SupplierShelf(root / "supplier.sqlite")
        candidate = owner.stage("weekly-parts", "v1", [{"part_number": "P-7", "quantity": 2}])
        try:
            owner.approve(candidate.key, candidate.version, candidate.digest, "Supplier P", "Maya",
                          lose_reply=True)
        except LostReply:
            print("approval reply lost after local commit")
        owner = OwnerLedger(root / "owner.sqlite")
        print("approval retry after reopen:", owner.approve(candidate.key, candidate.version,
              candidate.digest, "Supplier P", "Maya")["result"])
        try:
            shelf.accept(owner, candidate.key, candidate.version, "Supplier P", lose_reply=True)
        except LostReply:
            print("delivery reply lost after supplier's local commit")
        shelf = SupplierShelf(root / "supplier.sqlite")
        print("supplier lookup after reopen: verified =", shelf.lookup(candidate.key,
              candidate.version, "Supplier P")[1] == candidate.digest)
        owner.withdraw(candidate.key, candidate.version, "Maya")
        try:
            owner.approved_bytes(candidate.key, candidate.version, "Supplier P")
        except ExportDenied:
            print("future owner read after withdrawal: denied")
        print("supplier-held bytes after withdrawal: still present =", bool(shelf.lookup(
              candidate.key, candidate.version, "Supplier P")))


if __name__ == "__main__":
    run_demo()
