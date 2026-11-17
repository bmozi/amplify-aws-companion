"""Local HTTP visitor continuation for the two-store approval fixture.

All identities, approvals, bytes and destinations are fictional. No AWS calls.
"""

from contextlib import closing
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import sqlite3
import sys
import tempfile
import urllib.error
import urllib.request

from external_effect_lab import (ReplyLost, initialize, mark_unknown, prepare,
                                 publish, reconcile, state)
from two_reviewer_lab import admit, digest, review

OLD = b"Training price list revision 0\n"
NEW = b"Training price list revision 1\n"
DESTINATION = "training-site"


def action() -> dict:
    return {"id": "price-list-7", "revision": 1, "artifact": sha256(NEW).hexdigest(),
            "destination": DESTINATION, "effective_date": "fictional-day-2"}


def initialize_site(site: Path) -> None:
    with closing(sqlite3.connect(site)) as db, db:
        db.execute("CREATE TABLE current (destination TEXT PRIMARY KEY, digest TEXT, body BLOB)")
        db.execute("INSERT INTO current VALUES (?, ?, ?)",
                   (DESTINATION, sha256(OLD).hexdigest(), OLD))


def promote(local: Path, provider: Path, site: Path, proposed: dict, content: bytes) -> str:
    """A separate local step selects exactly the confirmed published bytes."""
    operation = f"publish:{proposed['id']}:{proposed['revision']}:{digest(proposed)}"
    if proposed["destination"] != DESTINATION or sha256(content).hexdigest() != proposed["artifact"]:
        return "NO_GO_CONTENT_OR_TARGET"
    with closing(sqlite3.connect(local)) as db:
        row = db.execute("SELECT digest,destination,artifact,state,receipt FROM dispatch WHERE operation=?",
                         (operation,)).fetchone()
    if row is None or row[:4] != (digest(proposed), DESTINATION, proposed["artifact"], "confirmed"):
        return "NO_GO_UNCONFIRMED"
    with closing(sqlite3.connect(provider)) as db:
        effect = db.execute("SELECT digest,destination,artifact,receipt FROM effects WHERE operation=?",
                            (operation,)).fetchone()
    if effect != (row[0], row[1], row[2], row[4]):
        return "NO_GO_PROVIDER_MISMATCH"
    with closing(sqlite3.connect(site)) as db, db:
        db.execute("UPDATE current SET digest=?,body=? WHERE destination=?",
                   (proposed["artifact"], content, DESTINATION))
        if db.execute("SELECT changes()").fetchone()[0] != 1:
            return "NO_GO_SITE_MISSING"
    return "PROMOTED"


def make_handler(site: Path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/training-site/prices":
                self.send_error(404)
                return
            with closing(sqlite3.connect(site)) as db:
                row = db.execute("SELECT digest,body FROM current WHERE destination=?",
                                 (DESTINATION,)).fetchone()
            if row is None or sha256(row[1]).hexdigest() != row[0]:
                self.send_error(503)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(row[1])))
            self.end_headers()
            self.wfile.write(row[1])

        def log_message(self, *args):
            pass

    return Handler


def fetch(base: str, path: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(base + path, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, b""


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="approval-visitor-") as folder:
        root = Path(folder)
        local, provider, site = (root / name for name in ("local.db", "publisher.db", "site.db"))
        proposed = action()
        initialize(local, provider, proposed)
        initialize_site(site)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(site))
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            before = fetch(base, "/training-site/prices")
            for reviewer in ("A", "B"):
                assert review(local, proposed["id"], reviewer, digest(proposed), 10, 100) == "reviewed"
            assert admit(local, proposed["id"], 20) == "admitted"
            operation = prepare(local, proposed)
            try:
                publish(provider, operation, proposed, lose_reply=True)
            except ReplyLost:
                mark_unknown(local, operation)
            after_provider_commit = fetch(base, "/training-site/prices")
            blocked = promote(local, provider, site, proposed, NEW)
            assert reconcile(local, provider, operation) == "confirmed"
            promoted = promote(local, provider, site, proposed, NEW)
            after_promotion = fetch(base, "/training-site/prices")
            wrong_destination = fetch(base, "/public-site/prices")
            assert before == (200, OLD) and after_provider_commit == (200, OLD)
            assert blocked == "NO_GO_UNCONFIRMED" and promoted == "PROMOTED"
            assert after_promotion == (200, NEW) and wrong_destination[0] == 404
            return {"approval_and_provider": state(local, operation),
                    "after_provider_commit": after_provider_commit[1].decode().strip(),
                    "pre_reconciliation_promotion": blocked,
                    "promotion": promoted,
                    "visitor_after_promotion": after_promotion[1].decode().strip(),
                    "wrong_destination_http": wrong_destination[0]}
        finally:
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()


if __name__ == "__main__":
    if sys.flags.optimize:
        raise SystemExit("Run without -O; this drill uses assertions")
    print(json.dumps(run(), indent=2))
