"""Loopback identity boundary for the A15 fictional export.

Opaque session values are issued and checked by this one local process. This
does not emulate Cognito, STS, SigV4, IAM, KMS, S3 or a supplier account.
"""

from contextlib import contextmanager
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import tempfile
import threading
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

from local_lab import ExportDenied
from persistent_lab import OwnerLedger, SupplierShelf


@contextmanager
def export_server(owner: OwnerLedger):
    """Yield a local URL and three ephemeral bearer values, then stop the server."""
    sessions = {secrets.token_urlsafe(32): ("owner", "Maya"),
                secrets.token_urlsafe(32): ("supplier", "Supplier P"),
                secrets.token_urlsafe(32): ("supplier", "Supplier Q")}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Never log a bearer value or the fictional export body.

        def reply(self, status, body):
            raw = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def principal(self):
            header = self.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return None
            return sessions.get(header.removeprefix("Bearer "))

        def do_POST(self):
            if self.path not in ("/approve", "/withdraw"):
                return self.reply(404, {"error": "unknown route"})
            who = self.principal()
            if who is None:
                return self.reply(401, {"error": "no valid local session"})
            if who[0] != "owner":
                return self.reply(403, {"error": "owner session required"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 2048:
                    return self.reply(400, {"error": "invalid request size"})
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict) or "actor" in body:
                    return self.reply(400, {"error": "actor comes from the session"})
                if self.path == "/approve":
                    if set(body) != {"key", "version", "digest", "supplier"}:
                        return self.reply(400, {"error": "invalid approval fields"})
                    receipt = owner.approve(body["key"], body["version"], body["digest"],
                                            body["supplier"], who[1])
                    return self.reply(200, receipt)
                if set(body) != {"key", "version"}:
                    return self.reply(400, {"error": "invalid withdrawal fields"})
                owner.withdraw(body["key"], body["version"], who[1])
                return self.reply(200, {"result": "future owner reads withdrawn"})
            except (ValueError, TypeError, json.JSONDecodeError):
                return self.reply(400, {"error": "malformed request"})
            except ExportDenied:
                return self.reply(403, {"error": "export denied"})

        def do_GET(self):
            parts = urlsplit(self.path)
            if parts.path != "/export":
                return self.reply(404, {"error": "unknown route"})
            who = self.principal()
            if who is None:
                return self.reply(401, {"error": "no valid local session"})
            if who[0] != "supplier":
                return self.reply(403, {"error": "supplier session required"})
            try:
                query = parse_qs(parts.query, strict_parsing=True)
            except ValueError:
                return self.reply(400, {"error": "exact key and version required"})
            if set(query) != {"key", "version"} or any(len(v) != 1 for v in query.values()):
                return self.reply(400, {"error": "exact key and version required"})
            try:
                payload, digest = owner.approved_bytes(query["key"][0], query["version"][0], who[1])
            except ExportDenied:
                return self.reply(403, {"error": "export denied"})
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("X-Content-SHA256", digest)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        owner_token = next(token for token, role in sessions.items() if role[0] == "owner")
        supplier_p_token = next(token for token, role in sessions.items() if role == ("supplier", "Supplier P"))
        supplier_q_token = next(token for token, role in sessions.items() if role == ("supplier", "Supplier Q"))
        yield f"http://127.0.0.1:{server.server_port}", owner_token, supplier_p_token, supplier_q_token
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def post(url, route, token, body):
    request = Request(url + route, data=json.dumps(body).encode(), method="POST",
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urlopen(request, timeout=3) as response:
        return json.load(response)


def fetch(url, token, key, version):
    request = Request(url + "/export?" + urlencode({"key": key, "version": version}),
                      headers={"Authorization": f"Bearer {token}"})
    with urlopen(request, timeout=3) as response:
        payload, digest = response.read(), response.headers["X-Content-SHA256"]
    if sha256(payload).hexdigest() != digest:
        raise ExportDenied("HTTP bytes do not match the response digest")
    return payload, digest


def run_demo():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        owner, shelf = OwnerLedger(root / "owner.sqlite"), SupplierShelf(root / "supplier.sqlite")
        c = owner.stage("weekly-parts", "v1", [{"part_number": "P-7", "quantity": 2}])
        with export_server(owner) as (url, owner_token, supplier_token, _other_supplier_token):
            try:
                post(url, "/approve", supplier_token,
                     {"key": c.key, "version": c.version, "digest": c.digest,
                      "supplier": "Supplier P", "actor": "Maya"})
            except HTTPError as error:
                print("forged body actor with supplier session: HTTP", error.code)
            approval = post(url, "/approve", owner_token,
                            {"key": c.key, "version": c.version, "digest": c.digest,
                             "supplier": "Supplier P"})
            payload, digest = fetch(url, supplier_token, c.key, c.version)
            shelf.accept_bytes(c.key, c.version, "Supplier P", payload, digest)
            print("owner approval:", approval["result"])
            print("supplier shelf verified:", shelf.lookup(c.key, c.version, "Supplier P")[1] == c.digest)
            post(url, "/withdraw", owner_token, {"key": c.key, "version": c.version})
            try:
                fetch(url, supplier_token, c.key, c.version)
            except HTTPError as error:
                print("new supplier read after withdrawal: HTTP", error.code)
            print("earlier supplier copy still present:", bool(shelf.lookup(c.key, c.version,
                                                                             "Supplier P")))


if __name__ == "__main__":
    run_demo()
