"""Synthetic booking endpoint: green probes can coexist with a wrong answer."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path == "/healthz":
            status, body = 200, {"process": "running"}
        elif self.path == "/readyz":
            status, body = 200, {"ready": True}
        elif self.path == "/bookings/42":
            status, body = 200, {"id": "42", "amount_cents": int(os.environ["BOOKING_AMOUNT"])}
        else:
            status, body = 404, {"error": "unknown path"}
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
