"""Loopback cache boundary fixture. It does not emulate CloudFront or authenticate callers."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class Fixture:
    def __init__(self, unsafe_private_cache=False):
        self.unsafe_private_cache = unsafe_private_cache
        self.origin_up = True
        self.public_cache = {}
        self.private_cache = {}
        self.invoices = {'alice': b'invoice-for-alice', 'bob': b'invoice-for-bob'}

    def serve(self, method, path, actor):
        """Return status, body, cache label; actor is a trusted TEST INPUT only."""
        if method == 'GET' and path == '/guide/warm':
            if path in self.public_cache:
                return 200, self.public_cache[path], 'public-hit'
            if not self.origin_up:
                return 503, b'origin-unavailable', 'origin-error'
            self.public_cache[path] = b'public-guide-v1'
            return 200, self.public_cache[path], 'public-fill'
        if method == 'GET' and path == '/guide/cold':
            if not self.origin_up:
                return 503, b'origin-unavailable', 'origin-error'
            return 200, b'uncached-guide', 'origin'
        if method == 'GET' and path == '/invoice/current':
            if self.unsafe_private_cache and path in self.private_cache:
                # Deliberate negative control: URL-only lookup precedes ownership check.
                return 200, self.private_cache[path], 'UNSAFE-private-hit'
            if actor not in self.invoices:
                return 403, b'forbidden', 'denied'
            if not self.origin_up:
                return 503, b'origin-unavailable', 'origin-error'
            body = self.invoices[actor]
            if self.unsafe_private_cache:
                self.private_cache[path] = body
                return 200, body, 'UNSAFE-private-fill'
            return 200, body, 'private-no-store'
        if method == 'POST' and path == '/booking':
            if not self.origin_up:
                return 503, b'booking-origin-unavailable', 'origin-error'
            return 202, b'synthetic-booking-accepted', 'origin'
        return 404, b'not-found', 'none'


def start_server(fixture):
    class Handler(BaseHTTPRequestHandler):
        def respond(self):
            status, body, cache = fixture.serve(self.command, self.path, self.headers.get('X-Fixture-Actor'))
            self.send_response(status)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            if self.path.startswith('/invoice/'):
                directive = 'public, max-age=300' if fixture.unsafe_private_cache else 'no-store'
            else:
                directive = 'max-age=300' if self.path == '/guide/warm' else 'no-store'
            self.send_header('Cache-Control', directive)
            self.send_header('X-Fixture-Cache', cache)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = respond
        do_POST = respond

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server, worker


def request(server, method, path, actor=None):
    headers = {'X-Fixture-Actor': actor} if actor is not None else {}
    url = f'http://127.0.0.1:{server.server_port}{path}'
    req = Request(url, method=method, headers=headers)
    try:
        response = urlopen(req, timeout=3)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read(), response.headers['X-Fixture-Cache']


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization so fixture assertions execute')
    unsafe = Fixture(unsafe_private_cache=True)
    server, worker = start_server(unsafe)
    try:
        alice = request(server, 'GET', '/invoice/current', 'alice')
        bob_leak = request(server, 'GET', '/invoice/current', 'bob')
        assert alice[1] == bob_leak[1] == b'invoice-for-alice'
        assert bob_leak[2] == 'UNSAFE-private-hit'
    finally:
        server.shutdown(); server.server_close(); worker.join()

    safe = Fixture()
    server, worker = start_server(safe)
    try:
        guide_fill = request(server, 'GET', '/guide/warm')
        alice_safe = request(server, 'GET', '/invoice/current', 'alice')
        bob_safe = request(server, 'GET', '/invoice/current', 'bob')
        unknown = request(server, 'GET', '/invoice/current', 'stranger')
        assert alice_safe[1] != bob_safe[1] and unknown[0] == 403
        safe.origin_up = False
        warm_during_outage = request(server, 'GET', '/guide/warm')
        cold_during_outage = request(server, 'GET', '/guide/cold')
        invoice_during_outage = request(server, 'GET', '/invoice/current', 'alice')
        booking_during_outage = request(server, 'POST', '/booking', 'alice')
        assert guide_fill[2] == 'public-fill' and warm_during_outage[2] == 'public-hit'
        assert [x[0] for x in (cold_during_outage, invoice_during_outage, booking_during_outage)] == [503] * 3
        print({'unsafe_cross_customer_leak_observed': bob_leak[1].decode(),
               'safe_alice': alice_safe[1].decode(), 'safe_bob': bob_safe[1].decode(),
               'stranger_status': unknown[0], 'warm_guide_during_outage': warm_during_outage[0],
               'cold_guide_during_outage': cold_during_outage[0],
               'invoice_during_outage': invoice_during_outage[0],
               'booking_during_outage': booking_during_outage[0],
               'scope': 'loopback fixture; header is trusted test input, not authentication or CDN behavior'})
    finally:
        server.shutdown(); server.server_close(); worker.join()


if __name__ == '__main__':
    main()
