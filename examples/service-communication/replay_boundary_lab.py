"""Cloud-free HTTP replay exercise with two invoice backend servers.

The signatures, identities and atomic in-memory ledgers are fictional fixtures.
They are not AWS IAM, TLS, distributed storage or a deployable replay design.
"""

from __future__ import annotations

from hmac import compare_digest
from http.server import BaseHTTPRequestHandler
import json
import secrets
from threading import Lock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from proxy_bypass_lab import INVOICES, proof, respond, server


class NonceLedger:
    def __init__(self):
        self._used: set[str] = set()
        self._lock = Lock()

    def claim(self, nonce: str) -> bool:
        with self._lock:
            if nonce in self._used:
                return False
            self._used.add(nonce)
            return True


def backend_handler(ledger: NonceLedger, proxy_secret: bytes,
                    customer_secret: bytes, fail_after_claim: bool = False):
    class Backend(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/invoices/INV-01":
                respond(self, 404, {"error": "unknown invoice"})
                return
            customer = self.headers.get("X-Customer-ID", "")
            nonce = self.headers.get("X-Proxy-Nonce", "")
            receipt = self.headers.get("X-Proxy-Receipt", "")
            customer_proof = self.headers.get("X-Customer-Proof", "")
            expected = proof(proxy_secret, f"GET|{self.path}|{customer}|{nonce}")
            owner = INVOICES["INV-01"]["customer"]
            authorized = (
                bool(nonce)
                and compare_digest(receipt, expected)
                and compare_digest(customer_proof,
                                   proof(customer_secret, f"{customer}|INV-01"))
                and compare_digest(customer, owner)
            )
            # Claim only after every ordinary authorization check. A denied
            # request must not consume a valid nonce belonging to its owner.
            if not authorized or not ledger.claim(nonce):
                respond(self, 403, {"error": "invoice denied"})
                return
            if fail_after_claim:
                # A consumed receipt does not establish that the intended
                # application result reached the caller.
                respond(self, 503, {"error": "result unavailable after claim"})
                return
            respond(self, 200, {"invoice": "INV-01", **INVOICES["INV-01"]})

        def log_message(self, *_args):
            pass

    return Backend


def entry_handler(backend_url: str, workload_key: str, proxy_secret: bytes,
                  capture: list[dict[str, str]]):
    class Entry(BaseHTTPRequestHandler):
        def do_GET(self):
            if not compare_digest(self.headers.get("X-Workload-Key", ""), workload_key):
                respond(self, 403, {"error": "service entry denied"})
                return
            customer = self.headers.get("X-Customer-ID", "")
            nonce = secrets.token_hex(16)
            headers = {
                "X-Customer-ID": customer,
                "X-Customer-Proof": self.headers.get("X-Customer-Proof", ""),
                "X-Proxy-Nonce": nonce,
                "X-Proxy-Receipt": proof(
                    proxy_secret, f"GET|{self.path}|{customer}|{nonce}"
                ),
            }
            # Instrumentation exposes the forwarded headers to this test only;
            # they are not returned to the HTTP caller.
            capture.append(headers.copy())
            request = Request(backend_url + self.path, headers=headers)
            try:
                with urlopen(request, timeout=5) as result:
                    respond(self, result.status, json.load(result))
            except HTTPError as error:
                respond(self, error.code, json.load(error))

        def log_message(self, *_args):
            pass

    return Entry


def get(base_url: str, headers: dict[str, str]) -> int:
    request = Request(base_url + "/invoices/INV-01", headers=headers)
    try:
        with urlopen(request, timeout=5) as result:
            return result.status
    except HTTPError as error:
        return error.code


def run_case(shared_ledger: bool) -> dict[str, int]:
    proxy_secret = secrets.token_bytes(32)
    customer_secret = secrets.token_bytes(32)
    workload_key = secrets.token_hex(24)
    ledger_a = NonceLedger()
    ledger_b = ledger_a if shared_ledger else NonceLedger()
    capture: list[dict[str, str]] = []
    customer_headers = {
        "X-Workload-Key": workload_key,
        "X-Customer-ID": "c-one",
        "X-Customer-Proof": proof(customer_secret, "c-one|INV-01"),
    }
    with server(backend_handler(ledger_a, proxy_secret, customer_secret)) as a:
        with server(backend_handler(ledger_b, proxy_secret, customer_secret)) as b:
            with server(entry_handler(a, workload_key, proxy_secret, capture)) as entry:
                first = get(entry, customer_headers)
                assert len(capture) == 1
                copied = capture[0]
                same_backend = get(a, copied)
                second_backend = get(b, copied)
                fresh_request = get(entry, customer_headers)
                return {
                    "first_via_entry": first,
                    "copied_to_same_backend": same_backend,
                    "copied_to_second_backend": second_backend,
                    "new_entry_request": fresh_request,
                    "direct_without_receipt": get(a, customer_headers),
                }


def main() -> None:
    result = {"separate_ledgers": run_case(False),
              "shared_ledger": run_case(True)}
    assert result == {
        "separate_ledgers": {
            "first_via_entry": 200,
            "copied_to_same_backend": 403,
            "copied_to_second_backend": 200,
            "new_entry_request": 200,
            "direct_without_receipt": 403,
        },
        "shared_ledger": {
            "first_via_entry": 200,
            "copied_to_same_backend": 403,
            "copied_to_second_backend": 403,
            "new_entry_request": 200,
            "direct_without_receipt": 403,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
