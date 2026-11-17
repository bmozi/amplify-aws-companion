"""Loopback HTTP model of a legacy application's per-node session and file state.

No AWS SDK, credentials, external address, or billable resource is used.
"""

from contextlib import ExitStack
import hashlib
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import shutil
import tempfile
from threading import Thread


HOST = "127.0.0.1"


class NodeState:
    def __init__(self, name, folder):
        self.name = name
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.sessions = set()

    def has_session(self, cookie):
        token = cookie.removeprefix("sid=").split(";", 1)[0]
        return token in self.sessions

    @property
    def file(self):
        return self.folder / "ticket.txt"


class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def reply(self, status, body=b"", content_type="text/plain", cookie=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)


class NodeHandler(QuietHandler):
    def do_GET(self):
        node = self.server.node
        if self.path == "/health":
            return self.reply(200, b"process responds")
        if self.path == "/inventory":
            if self.headers.get("X-Lab-Operator") != "local":
                return self.reply(403, b"operator header required")
            body = json.dumps({
                "node": node.name,
                "sessions": len(node.sessions),
                "file_present": node.file.exists(),
                "file_sha256": hashlib.sha256(node.file.read_bytes()).hexdigest() if node.file.exists() else None,
            }).encode()
            return self.reply(200, body, "application/json")
        if not node.has_session(self.headers.get("Cookie", "")):
            return self.reply(401, b"session not found on this node")
        if self.path == "/me":
            return self.reply(200, f"signed in on {node.name}".encode())
        if self.path == "/file":
            return self.reply(200, node.file.read_bytes()) if node.file.exists() else self.reply(404, b"file absent")
        self.reply(404, b"unknown path")

    def do_POST(self):
        node = self.server.node
        if self.path == "/login":
            token = secrets.token_urlsafe(18)
            node.sessions.add(token)
            return self.reply(200, b"local login accepted", cookie=f"sid={token}; HttpOnly; SameSite=Lax")
        if self.path != "/upload":
            return self.reply(404, b"unknown path")
        if not node.has_session(self.headers.get("Cookie", "")):
            return self.reply(401, b"session not found on this node")
        size = int(self.headers.get("Content-Length", "0"))
        if size < 1 or size > 4096:
            return self.reply(400, b"file must be 1 to 4096 bytes")
        node.file.write_bytes(self.rfile.read(size))
        self.reply(201, b"stored on this node")


class ProxyHandler(QuietHandler):
    def do_GET(self):
        self.forward()

    def do_POST(self):
        self.forward()

    def forward(self):
        target = self.server.target
        if target is None:
            return self.reply(503, b"no selected target")
        connection = HTTPConnection(HOST, target, timeout=2)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(size) if size else None
            headers = {}
            for name in ("Cookie", "Content-Length", "X-Lab-Operator"):
                if self.headers.get(name):
                    headers[name] = self.headers[name]
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
            data = response.read()
            self.reply(response.status, data, response.getheader("Content-Type", "text/plain"), response.getheader("Set-Cookie"))
        except OSError:
            self.reply(503, b"selected target unavailable")
        finally:
            connection.close()


class LocalLab:
    def __enter__(self):
        self.stack = ExitStack()
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix="legacy-failover-")))
        self.primary = NodeState("A", self.root / "A")
        self.standby = NodeState("B", self.root / "B")
        self.servers = []
        self.primary_stopped = False
        self.a_server = self._serve(NodeHandler, self.primary)
        self.b_server = self._serve(NodeHandler, self.standby)
        self.proxy = self._serve(ProxyHandler)
        self.proxy.target = self.a_server.server_address[1]
        return self

    def _serve(self, handler, node=None):
        server = ThreadingHTTPServer((HOST, 0), handler)
        if node is not None:
            server.node = node
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.servers.append((server, thread))
        return server

    def select_standby(self):
        self.proxy.target = self.b_server.server_address[1]

    def stop_primary(self):
        if not self.primary_stopped:
            self.a_server.shutdown()
            self.a_server.server_close()
            self.primary_stopped = True

    def copy_upload_to_standby(self):
        shutil.copy2(self.primary.file, self.standby.file)

    def request(self, method, path, *, cookie=None, data=None, operator=False):
        connection = HTTPConnection(HOST, self.proxy.server_address[1], timeout=3)
        headers = {}
        if cookie:
            headers["Cookie"] = cookie.split(";", 1)[0]
        if operator:
            headers["X-Lab-Operator"] = "local"
        connection.request(method, path, body=data, headers=headers)
        response = connection.getresponse()
        result = response.status, response.getheader("Set-Cookie"), response.read()
        connection.close()
        return result

    def __exit__(self, *_exc):
        for server, thread in reversed(self.servers):
            if server is not self.a_server or not self.primary_stopped:
                server.shutdown()
                server.server_close()
            thread.join(timeout=2)
        self.stack.close()


def run_demo():
    with LocalLab() as lab:
        _, cookie, _ = lab.request("POST", "/login")
        upload = lab.request("POST", "/upload", cookie=cookie, data=b"booking-241-photo")
        before = lab.request("GET", "/file", cookie=cookie)
        lab.stop_primary()
        lab.select_standby()
        standby_health = lab.request("GET", "/health")
        old_session = lab.request("GET", "/me", cookie=cookie)
        missing_file = json.loads(lab.request("GET", "/inventory", operator=True)[2])["file_present"]
        lab.copy_upload_to_standby()
        copied_file = json.loads(lab.request("GET", "/inventory", operator=True)[2])["file_present"]
        still_old_session = lab.request("GET", "/me", cookie=cookie)
        _, new_cookie, _ = lab.request("POST", "/login")
        new_session_file = lab.request("GET", "/file", cookie=new_cookie)
        return {
            "upload_status_on_A": upload[0],
            "owner_file_before_failure": before[0],
            "standby_health_after_switch": standby_health[0],
            "old_session_on_B": old_session[0],
            "file_on_B_before_copy": missing_file,
            "file_on_B_after_copy": copied_file,
            "old_session_after_file_copy": still_old_session[0],
            "new_session_file_after_copy": new_session_file[0],
            "scope": "Loopback proxy and two in-process HTTP nodes; not AWS ALB, real identity, durable shared storage or regional failover",
        }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
