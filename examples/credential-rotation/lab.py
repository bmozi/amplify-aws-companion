"""Sequential local HTTP credential lifecycle; synthetic values, no AWS or TLS."""
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
import threading
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

# Public fixtures, deliberately not usable credentials. Never substitute real values.
A = 'public-fixture-credential-A'
B = 'public-fixture-credential-B'
C = 'public-fixture-credential-C'
OPENER = build_opener(ProxyHandler({}))  # Local requests must not use environment proxies.


@dataclass
class Fixture:
    stored: str = A
    accepted: str = A
    accepted_also: str | None = None
    store_available: bool = True
    supplier_available: bool = True
    reads: int = 0
    calls: int = 0


class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@contextmanager
def services(state):
    class Store(QuietHandler):
        def do_GET(self):
            if self.path != '/credential':
                self.reply(404, {}); return
            state.reads += 1
            if not state.store_available:
                self.reply(503, {}); return
            self.reply(200, {'value': state.stored})

    class Supplier(QuietHandler):
        def do_GET(self):
            if self.path != '/availability':
                self.reply(404, {}); return
            state.calls += 1
            if not state.supplier_available:
                self.reply(503, {}); return
            presented = self.headers.get('Authorization')
            permitted = presented in {'Bearer ' + value for value in (state.accepted, state.accepted_also) if value is not None}
            self.reply(200 if permitted else 401, {'available': True} if permitted else {})

    servers = []
    try:
        for handler in (Store, Supplier):
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            servers.append((server, thread))
        yield tuple(f'http://127.0.0.1:{server.server_port}' for server, _ in servers)
    finally:
        for server, thread in reversed(servers):
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            assert not thread.is_alive()


def get(url, credential=None):
    headers = {} if credential is None else {'Authorization': 'Bearer ' + credential}
    try:
        with OPENER.open(Request(url, headers=headers), timeout=2) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        with error:
            return error.code, json.load(error)


class Worker:
    """One credential refresh and at most one retry of this read-only operation."""
    def __init__(self, store, supplier, ttl=10):
        self.store = store
        self.supplier = supplier
        self.ttl = ttl
        self.cached = None
        self.expires = 0

    def refresh(self, now):
        # Once refresh is required, a failed read cannot resurrect a stale credential.
        self.cached = None
        status, body = get(self.store + '/credential')
        if status != 200:
            return False
        self.cached = body['value']
        self.expires = now + self.ttl
        return True

    def availability(self, now):
        # The caller supplies a monotonic teaching clock so expiry tests need no sleep.
        if self.cached is None or now >= self.expires:
            if not self.refresh(now):
                return 'secret_unavailable'
        status, _ = get(self.supplier + '/availability', self.cached)
        if status == 401:
            if not self.refresh(now):
                return 'secret_unavailable'
            status, _ = get(self.supplier + '/availability', self.cached)
            if status == 401:
                self.cached = None
        return {200: 'ok', 401: 'unauthorized', 503: 'supplier_unavailable'}.get(status, 'unexpected')


def main():
    if sys.flags.optimize:
        raise SystemExit('Run without -O: this exercise uses assertions.')
    state = Fixture()
    observations = []
    with services(state) as (store, supplier):
        worker = Worker(store, supplier)

        def observe(label, now, expected, reads, calls):
            before = state.reads, state.calls
            result = worker.availability(now)
            actual = state.reads - before[0], state.calls - before[1]
            assert result == expected, (label, result, expected)
            assert actual == (reads, calls), (label, actual, (reads, calls))
            observations.append({'case': label, 'result': result,
                                 'secret_reads': actual[0], 'supplier_calls': actual[1]})

        observe('initial access', 0, 'ok', 1, 1)
        # Store-only update is not successful rotation: supplier still accepts A.
        state.stored = B
        observe('store changed but target unchanged; expired cache', 10, 'unauthorized', 2, 2)
        state.accepted = B
        observe('target now agrees with stored credential', 11, 'ok', 1, 1)
        # A completed replacement leaves this worker holding B until rejection/refresh.
        state.stored = state.accepted = C
        observe('warm worker refreshes after rejection', 12, 'ok', 1, 2)
        state.supplier_available = False
        observe('supplier outage is not an authentication retry', 13, 'supplier_unavailable', 0, 1)
        state.supplier_available = True
        state.store_available = False
        observe('unexpired cache works while store unavailable', 14, 'ok', 0, 1)
        observe('expired cache cannot be refreshed', 22, 'secret_unavailable', 1, 0)
        assert worker.cached is None
        state.store_available = True
        observe('store recovery restores access', 23, 'ok', 1, 1)
        state.accepted = B
        state.store_available = False
        observe('rejected cache and unavailable store', 24, 'secret_unavailable', 1, 1)
        assert worker.cached is None
        state.store_available = True
        # Stored C is still wrong. Two attempts fail; there is no endless refresh loop.
        observe('persistent mismatch is bounded', 25, 'unauthorized', 2, 2)
        assert worker.cached is None
        state.stored = B
        observe('reconciled target and store recover', 26, 'ok', 1, 1)
        # Explicitly verify old C no longer works; a green request alone cannot prove this.
        status, _ = get(supplier + '/availability', C)
        assert status == 401
        observations.append({'case': 'old credential rejected directly', 'http_status': status})
    # A separate two-worker run makes the overlap contract observable. It is a
    # generic supplier fixture, not Secrets Manager's alternating-user flow.
    overlap = Fixture()
    with services(overlap) as (store, supplier):
        old_worker = Worker(store, supplier, ttl=10)
        new_worker = Worker(store, supplier, ttl=10)
        assert old_worker.availability(0) == 'ok'
        overlap.stored = B
        # Publishing B before the supplier accepts it must not retire A.
        assert new_worker.availability(1) == 'unauthorized'
        assert old_worker.availability(1) == 'ok'
        overlap.stored = A
        assert old_worker.availability(2) == 'ok'
        observations.append({'case': 'failed pending value leaves old worker usable', 'result': 'old_ok_new_denied'})
        # Add B at the supplier first, then publish and prove it at both workers.
        overlap.accepted_also = B
        overlap.stored = B
        assert new_worker.availability(3) == 'ok'
        assert old_worker.availability(3) == 'ok'  # its old cached A is still valid
        assert old_worker.cached == A and new_worker.cached == B
        assert old_worker.availability(10) == 'ok'  # expiry forces a B refresh
        assert old_worker.cached == B and new_worker.cached == B
        observations.append({'case': 'overlap allows old and new worker, then refreshes both', 'result': 'ok'})
        # Retirement is a separate target-side decision, verified negatively.
        overlap.accepted = B
        overlap.accepted_also = None
        assert old_worker.availability(11) == 'ok'
        assert new_worker.availability(11) == 'ok'
        old_status, _ = get(supplier + '/availability', A)
        assert old_status == 401
        observations.append({'case': 'retirement preserves new workers and rejects old value', 'result': 'ok', 'old_http_status': old_status})
    output = json.dumps({'result': 'passed', 'observations': observations,
                         'scope': 'Sequential loopback HTTP including two workers and an overlap round; synthetic store and supplier; injected expiry clock; no AWS or TLS'}, indent=2)
    assert all(value not in output for value in (A, B, C))
    print(output)


if __name__ == '__main__':
    main()
