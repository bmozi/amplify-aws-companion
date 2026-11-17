"""Cloud-free HTTP fixture for a proxy bypass and customer-record denial.

All credentials here are synthetic, generated inside this process. They are not
AWS IAM, TLS, a production identity scheme, or a deployable proxy policy.
"""

from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
from hmac import compare_digest, new as hmac_new
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import secrets
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen


INVOICES = {"INV-01": {"customer": "c-one", "total_cents": 900}}


def proof(secret: bytes, message: str) -> str:
    return hmac_new(secret, message.encode("utf-8"), sha256).hexdigest()


def respond(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    data = json.dumps(body, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def backend_handler(guarded: bool, proxy_secret: bytes, customer_secret: bytes):
    class Backend(BaseHTTPRequestHandler):
        def do_GET(self):
            if not self.path.startswith("/invoices/") or "?" in self.path:
                respond(self, 404, {"error": "unknown route"})
                return
            invoice_id = self.path.removeprefix("/invoices/")
            invoice = INVOICES.get(invoice_id)
            if invoice is None:
                respond(self, 404, {"error": "unknown invoice"})
                return
            customer = self.headers.get("X-Customer-ID", "")
            if guarded:
                expected_path = proof(proxy_secret, f"GET|{self.path}|{customer}")
                expected_customer = proof(customer_secret, f"{customer}|{invoice_id}")
                path_ok = compare_digest(self.headers.get("X-Proxy-Receipt", ""), expected_path)
                customer_ok = compare_digest(
                    self.headers.get("X-Customer-Proof", ""), expected_customer
                )
                owner_ok = compare_digest(customer, invoice["customer"])
                if not (path_ok and customer_ok and owner_ok):
                    respond(self, 403, {"error": "invoice denied"})
                    return
            respond(self, 200, {"invoice": invoice_id, **invoice})

        def log_message(self, *_args):
            pass

    return Backend


def proxy_handler(backend_url: str, workload_key: str, proxy_secret: bytes):
    class Proxy(BaseHTTPRequestHandler):
        def do_GET(self):
            if not compare_digest(self.headers.get("X-Workload-Key", ""), workload_key):
                respond(self, 403, {"error": "service entry denied"})
                return
            customer = self.headers.get("X-Customer-ID", "")
            # Strip caller-supplied proxy receipts; only this fixture's proxy signs.
            headers = {
                "X-Customer-ID": customer,
                "X-Customer-Proof": self.headers.get("X-Customer-Proof", ""),
                "X-Proxy-Receipt": proof(proxy_secret, f"GET|{self.path}|{customer}"),
            }
            request = Request(backend_url + self.path, headers=headers)
            try:
                with urlopen(request, timeout=5) as result:
                    respond(self, result.status, json.load(result))
            except HTTPError as error:
                respond(self, error.code, json.load(error))

        def log_message(self, *_args):
            pass

    return Proxy


@contextmanager
def server(handler_type):
    instance = ThreadingHTTPServer(("127.0.0.1", 0), handler_type)
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{instance.server_port}"
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def get(url: str, headers: dict[str, str] | None = None) -> int:
    request = Request(url + "/invoices/INV-01", headers=headers or {})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status
    except HTTPError as error:
        return error.code


def run_case(guarded: bool) -> dict[str, int]:
    proxy_secret = secrets.token_bytes(32)
    customer_secret = secrets.token_bytes(32)
    workload_key = secrets.token_hex(24)

    def customer_headers(customer: str) -> dict[str, str]:
        return {
            "X-Workload-Key": workload_key,
            "X-Customer-ID": customer,
            "X-Customer-Proof": proof(customer_secret, f"{customer}|INV-01"),
        }

    with server(backend_handler(guarded, proxy_secret, customer_secret)) as backend:
        with server(proxy_handler(backend, workload_key, proxy_secret)) as entry:
            right_customer = customer_headers("c-one")
            wrong_customer = customer_headers("c-two")
            return {
                "permitted_via_entry": get(entry, right_customer),
                "wrong_workload_via_entry": get(entry, {"X-Workload-Key": "reporter"}),
                "wrong_customer_via_entry": get(entry, wrong_customer),
                "direct_backend_with_customer_proof": get(backend, right_customer),
                "direct_backend_with_fake_proxy_receipt": get(
                    backend, {**right_customer, "X-Proxy-Receipt": "forged"}
                ),
                # A copied valid receipt still works: this toy does not close
                # network reachability, confidentiality, freshness, or replay.
                "direct_backend_with_copied_valid_receipt": get(
                    backend,
                    {
                        **right_customer,
                        "X-Proxy-Receipt": proof(
                            proxy_secret, "GET|/invoices/INV-01|c-one"
                        ),
                    },
                ),
            }


def main() -> None:
    result = {"unguarded": run_case(False), "guarded": run_case(True)}
    expected = {
        "unguarded": {
            "permitted_via_entry": 200,
            "wrong_workload_via_entry": 403,
            "wrong_customer_via_entry": 200,
            "direct_backend_with_customer_proof": 200,
            "direct_backend_with_fake_proxy_receipt": 200,
            "direct_backend_with_copied_valid_receipt": 200,
        },
        "guarded": {
            "permitted_via_entry": 200,
            "wrong_workload_via_entry": 403,
            "wrong_customer_via_entry": 403,
            "direct_backend_with_customer_proof": 403,
            "direct_backend_with_fake_proxy_receipt": 403,
            "direct_backend_with_copied_valid_receipt": 200,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if result != expected:
        raise SystemExit("The expected entry, bypass, or customer boundary changed")


if __name__ == "__main__":
    main()
