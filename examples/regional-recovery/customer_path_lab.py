"""Local customer-path recovery drill. No AWS replication, DNS, or distributed fence."""

from contextlib import closing
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import sqlite3
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def rows(path):
    with closing(sqlite3.connect(path)) as db:
        return dict(db.execute("SELECT id, amount_cents FROM bookings ORDER BY id"))


def put(path, booking_id, amount):
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("INSERT INTO bookings VALUES (?, ?)", (booking_id, amount))


class Recovery:
    def __init__(self, folder):
        self.source = Path(folder) / "source.sqlite"
        self.candidate = Path(folder) / "candidate.sqlite"
        with closing(sqlite3.connect(self.source)) as db, db:
            db.execute("CREATE TABLE bookings (id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL CHECK(amount_cents > 0))")
            db.execute("INSERT INTO bookings VALUES ('110', 1200)")
        # An actual local database copy is made before booking 111 is confirmed.
        with closing(sqlite3.connect(self.source)) as src, closing(sqlite3.connect(self.candidate)) as dst:
            src.backup(dst)
        put(self.source, "111", 2300)
        self.journal = {"110": 1200, "111": 2300}  # fictional independent authority
        self.source_online = False
        self.source_writable = True
        self.key_available = False
        self.route = "source"
        self.candidate_writable = False
        self.candidate_online = True

    def health(self, location):
        return self.candidate_online if location == "candidate" else self.source_online

    def booking_at(self, location, booking_id):
        """Read one named location; a pinned client need not follow the route."""
        if location not in ("source", "candidate"):
            raise ValueError("Unknown recovery location")
        if not self.health(location):
            return 503, {"error": f"{location} unavailable"}
        found = rows(self.source if location == "source" else self.candidate)
        if booking_id not in found:
            return 404, {"error": "booking absent"}
        return 200, {"id": booking_id, "amount_cents": found[booking_id]}

    def booking(self, booking_id):
        return self.booking_at(self.route, booking_id)

    def bridge_target(self, booking_id):
        """Local read-only redirect gate; no identity or real writer fencing."""
        if not booking_id or not booking_id.isascii() or not booking_id.isdigit():
            return 400, {"error": "invalid booking id"}
        if (not self.source_online or self.route != "candidate" or
                self.source_writable or not self.health("candidate")):
            return 503, {"error": "bridge not ready"}
        status, _ = self.booking_at("candidate", booking_id)
        if status != 200:
            return status, {"error": "booking not available on candidate"}
        return 307, {"location": f"/bookings/{booking_id}"}

    def reconcile(self):
        actual = rows(self.candidate)
        return {
            "missing": sorted(set(self.journal) - set(actual)),
            "unexpected": sorted(set(actual) - set(self.journal)),
            "changed": sorted(k for k in actual.keys() & self.journal.keys()
                              if actual[k] != self.journal[k]),
        }

    def replay_missing(self):
        if self.candidate_writable:
            raise ValueError("Close candidate writes before replay")
        difference = self.reconcile()
        if difference["unexpected"] or difference["changed"]:
            raise ValueError("Candidate differs from trusted journal")
        with closing(sqlite3.connect(self.candidate)) as db, db:
            for key in difference["missing"]:
                db.execute("INSERT INTO bookings VALUES (?, ?)", (key, self.journal[key]))
        return self.reconcile()

    def switch(self):
        if not self.key_available:
            raise ValueError("Recovery key has not been tested")
        if self.source_writable:
            raise ValueError("Old writer is not fenced")
        if self.reconcile() != {"missing": [], "unexpected": [], "changed": []}:
            raise ValueError("Candidate does not match confirmed bookings")
        if not self.health("candidate") or rows(self.candidate).get("111") != self.journal["111"]:
            raise ValueError("Customer read path is not ready")
        self.route = "candidate"
        self.candidate_writable = True

    def accept(self, booking_id, amount):
        if self.route != "candidate" or not self.candidate_writable:
            return 503, {"error": "writes paused"}
        if not isinstance(booking_id, str) or not booking_id.isdigit() or type(amount) is not int or amount <= 0:
            return 400, {"error": "invalid booking"}
        try:
            put(self.candidate, booking_id, amount)
        except sqlite3.IntegrityError:
            return 409, {"error": "booking already exists"}
        self.journal[booking_id] = amount
        return 201, {"id": booking_id, "amount_cents": amount}

    def return_to_source(self):
        if rows(self.source) != self.journal:
            raise ValueError("Source lacks confirmed candidate work; reconcile before return")
        raise ValueError("No tested reverse writer handoff in this drill")


def handler_for(recovery):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def answer(self, status, body):
            data = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/candidate/health":
                return self.answer(200, {"healthy": recovery.health("candidate")})
            if self.path.startswith("/pinned-source/bookings/"):
                status, body = recovery.booking_at(
                    "source", self.path.removeprefix("/pinned-source/bookings/"))
                return self.answer(status, body)
            if self.path.startswith("/pinned-source-bridge/bookings/"):
                status, body = recovery.bridge_target(
                    self.path.removeprefix("/pinned-source-bridge/bookings/"))
                if status == 307:
                    data = json.dumps(body).encode()
                    self.send_response(status)
                    self.send_header("Location", body["location"])
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    return self.wfile.write(data)
                return self.answer(status, body)
            if self.path.startswith("/bookings/"):
                status, body = recovery.booking(self.path.removeprefix("/bookings/"))
                return self.answer(status, body)
            self.answer(404, {"error": "unknown path"})

        def do_POST(self):
            if self.path != "/bookings":
                return self.answer(404, {"error": "unknown path"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 1024:
                    raise ValueError("bad size")
                body = json.loads(self.rfile.read(length))
                status, result = recovery.accept(body["id"], body["amount_cents"])
            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                status, result = 400, {"error": "invalid request"}
            self.answer(status, result)

    return Handler


def request(base, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        with error:
            return error.code, json.load(error)


def raw_get(base, path):
    """Observe a client that does not automatically follow a redirect."""
    from urllib.parse import urlsplit
    endpoint = urlsplit(base)
    with closing(HTTPConnection(endpoint.hostname, endpoint.port, timeout=3)) as connection:
        connection.request("GET", path)
        response = connection.getresponse()
        return response.status, response.getheader("Location"), json.load(response)


def run():
    with tempfile.TemporaryDirectory(prefix="amplify-customer-recovery-") as folder:
        recovery = Recovery(folder)
        with ThreadingHTTPServer(("127.0.0.1", 0), handler_for(recovery)) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                before = {"candidate_health": request(base, "/candidate/health"),
                          "customer_read": request(base, "/bookings/111"),
                          "candidate_difference": recovery.reconcile()}
                recovery.source_writable = False  # cooperative flag, not an AWS fence
                recovery.key_available = True       # fictional check, not KMS evidence
                replay = recovery.replay_missing()
                recovery.switch()
                after = {"customer_read": request(base, "/bookings/111"),
                         "new_booking": request(base, "/bookings", {"id": "112", "amount_cents": 900}),
                         "new_booking_read": request(base, "/bookings/112")}
                recovery.source_online = True  # old endpoint returns; route stays on candidate
                pinned_client = {
                    "old_booking": request(base, "/pinned-source/bookings/111"),
                    "new_booking": request(base, "/pinned-source/bookings/112"),
                    "current_route_new_booking": request(base, "/bookings/112"),
                }
                bridge_path = "/pinned-source-bridge/bookings/112"
                bridge = {
                    "nonfollowing_client": raw_get(base, bridge_path),
                    "following_client": request(base, bridge_path),
                    "write_attempt": request(base, bridge_path, {"id": "113", "amount_cents": 100}),
                }
                recovery.candidate_online = False
                bridge["candidate_unavailable"] = raw_get(base, bridge_path)
                recovery.candidate_online = True
                try:
                    recovery.return_to_source()
                except ValueError as error:
                    failback = str(error)
            finally:
                server.shutdown()
                thread.join(timeout=3)
                if thread.is_alive():
                    raise RuntimeError("Loopback server did not stop")
        return {"before": before, "replay_difference": replay, "after": after,
                "pinned_client_after_old_endpoint_returns": pinned_client,
                "read_only_bridge": bridge,
                "failback": failback,
                "scope": "Loopback HTTP and temporary SQLite; a deliberately pinned old-endpoint route, cooperative fence and fictional journal/key; no AWS, DNS, external effects or regional RTO/RPO"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
