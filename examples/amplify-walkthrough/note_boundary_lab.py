"""Loopback-only illustration of a hidden list versus a direct owner check.

The X-Lab-Actor header is a forgeable fixture label, never authentication.
This server does not implement Amplify, AppSync or Cognito.
"""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen


NOTES = {"note-1": {"id": "note-1", "owner": "alice", "text": "Alice's synthetic note"}}
ACTORS = {"alice", "bob"}


def handler_for(enforce_owner, conceal_existence=False):
    if conceal_existence and not enforce_owner:
        raise ValueError("Concealment requires the owner check in this fixture")
    class NoteHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            actor = self.headers.get("X-Lab-Actor")
            if actor not in ACTORS:
                self.reply(401, {"error": "synthetic actor required"})
                return
            if self.path == "/notes":
                self.reply(200, {"items": [note for note in NOTES.values() if note["owner"] == actor]})
                return
            if self.path.startswith("/notes/") and self.path.count("/") == 2:
                note = NOTES.get(self.path.rsplit("/", 1)[1])
                if note is None:
                    self.reply(404, {"error": "unknown note"})
                elif enforce_owner and note["owner"] != actor:
                    if conceal_existence:
                        self.reply(404, {"error": "unknown note"})
                    else:
                        self.reply(403, {"error": "owner check denied"})
                else:
                    self.reply(200, note)
                return
            self.reply(404, {"error": "unknown path"})

        def reply(self, status, payload):
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    return NoteHandler


@contextmanager
def local_api(enforce_owner, conceal_existence=False):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(enforce_owner, conceal_existence))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def get(base, path, actor=None):
    headers = {"X-Lab-Actor": actor} if actor is not None else {}
    request = Request(base + path, headers=headers)
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        with error:
            return error.code, json.load(error)


def observe(enforce_owner, conceal_existence=False):
    with local_api(enforce_owner, conceal_existence) as base:
        return {
            "bob_list": get(base, "/notes", "bob"),
            "bob_direct_get": get(base, "/notes/note-1", "bob"),
            "bob_unknown_get": get(base, "/notes/not-a-note", "bob"),
            "alice_direct_get": get(base, "/notes/note-1", "alice"),
            "anonymous_direct_get": get(base, "/notes/note-1"),
            "bob_claims_alice_header_get": get(base, "/notes/note-1", "alice"),
        }


def main():
    print(json.dumps({
        "unsafe_list_filter_only": observe(False),
        "server_owner_check": observe(True),
        "owner_check_matching_response": observe(True, conceal_existence=True),
        "identity_limit": "X-Lab-Actor is a forgeable fixture label, not a signed identity",
    }, indent=2))


if __name__ == "__main__":
    main()
