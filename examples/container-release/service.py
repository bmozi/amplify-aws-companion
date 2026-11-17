"""Teaching HTTP service; no authentication, persistence or production web server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
import signal
import threading
import time
from urllib.parse import parse_qs, urlsplit

stopped = threading.Event()
held = threading.Event()
working = threading.Event()
accept_loop_stopped = threading.Event()


class DrainingServer(ThreadingHTTPServer):
    # Wait for request handlers after stopping the accept loop.
    daemon_threads = False
    block_on_close = True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ready = os.environ.get('READY', 'yes') == 'yes' and not stopped.is_set()
        parsed = urlsplit(self.path)
        if self.path == '/live':
            status, body = 200, {'alive': True}
        elif self.path == '/ready':
            status, body = (200 if ready else 503), {'ready': ready}
        elif self.path == '/state':
            status, body = 200, {'held': held.is_set(), 'working': working.is_set()}
        elif parsed.path == '/work' and not ready:
            status, body = 503, {'error': 'not ready'}
        elif parsed.path == '/work' and ready:
            try:
                inputs = parse_qs(parsed.query, strict_parsing=True)
                if set(inputs) != {'duration_ms'} or len(inputs['duration_ms']) != 1:
                    raise ValueError('expected one duration')
                duration_ms = int(inputs['duration_ms'][0])
                if not 0 <= duration_ms <= 10000:
                    raise ValueError('duration outside fixture bounds')
            except (ValueError, KeyError):
                status, body = 400, {'error': 'invalid work duration'}
            else:
                working.set()
                print('work_started', duration_ms, flush=True)
                # A bounded computation that continues independently of SIGTERM.
                # It has no stored or external effect.
                digest = b'local teaching work'
                finish_at = time.monotonic() + duration_ms / 1000
                while time.monotonic() < finish_at:
                    digest = hashlib.sha256(digest).digest()
                status, body = 200, {'release': os.environ['RELEASE'], 'work_ms': duration_ms}
        elif self.path == '/held' and ready:
            # Controlled fixture: completion becomes possible only after SIGTERM.
            held.set()
            print('request_started', flush=True)
            if not stopped.wait(timeout=15):
                status, body = 504, {'error': 'fixture was not released'}
            else:
                accept_loop_stopped.wait(timeout=5)
                time.sleep(1)  # Controlled work after the accept loop has ended.
                status, body = 200, {'release': os.environ['RELEASE'], 'completed': True}
        elif parsed.path == '/invoice' and not ready:
            status, body = 503, {'error': 'not ready'}
        elif parsed.path == '/invoice':
            try:
                inputs = parse_qs(parsed.query, strict_parsing=True)
                if set(inputs) != {'subtotal_cents', 'discount_cents'}:
                    raise ValueError('expected exactly two amounts')
                subtotal = int(inputs['subtotal_cents'][0])
                discount = int(inputs['discount_cents'][0])
                if len(inputs['subtotal_cents']) != 1 or len(inputs['discount_cents']) != 1 or not 0 <= discount <= subtotal <= 100000:
                    raise ValueError('invalid amount')
            except (ValueError, KeyError):
                status, body = 400, {'error': 'invalid invoice inputs'}
            else:
                applied_discount = 0 if os.environ.get('INVOICE_MODE') == 'omit-discount' else discount
                status, body = 200, {'release': os.environ['RELEASE'], 'total_cents': subtotal - applied_discount}
        elif self.path == '/':
            status, body = (200 if ready else 503), {'release': os.environ['RELEASE']}
        else:
            status, body = 404, {'error': 'not found'}
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        if self.path == '/held':
            self.wfile.flush()
            print('request_completed', flush=True)
            held.clear()
        elif parsed.path == '/work' and status == 200:
            self.wfile.flush()
            print('work_completed', flush=True)
            working.clear()

    def log_message(self, *args):
        pass


def main():
    server = DrainingServer((os.environ.get('BIND_HOST', '0.0.0.0'),
                             int(os.environ.get('PORT', '8080'))), Handler)
    def terminate(*_):
        print('termination_received', flush=True)
        stopped.set()
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, lambda *_: stopped.set())
    worker = threading.Thread(target=server.serve_forever)
    worker.start()
    print('started', os.environ['RELEASE'], flush=True)
    stopped.wait()
    server.shutdown()
    worker.join()
    accept_loop_stopped.set()
    server.server_close()
    print('graceful_stop', flush=True)


if __name__ == '__main__':
    main()
