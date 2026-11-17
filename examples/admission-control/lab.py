"""One-slot admission control over actual loopback HTTP; no AWS calls."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import BoundedSemaphore, Event, Thread
from urllib.error import HTTPError
from urllib.request import urlopen
import json


def run():
    slot = BoundedSemaphore(1)
    entered, release = Event(), Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status, message):
            payload = message.encode()
            self.send_response(status)
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            if self.path == '/live':
                self.reply(200, 'process responding')
                return
            if self.path not in ('/work', '/hold', '/fail'):
                self.reply(404, 'unknown route')
                return
            if not slot.acquire(blocking=False):
                self.reply(503, 'capacity unavailable; work not accepted')
                return
            try:
                if self.path == '/hold':
                    entered.set()
                    if not release.wait(5):
                        self.reply(504, 'fixture release timed out')
                        return
                if self.path == '/fail':
                    raise RuntimeError('injected worker failure')
                self.reply(200, 'work completed')
            except RuntimeError:
                self.reply(500, 'work failed')
            finally:
                slot.release()

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = False
    thread = Thread(target=server.serve_forever)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'

    def get(path):
        try:
            with urlopen(base + path, timeout=3) as response:
                return response.status, response.read().decode()
        except HTTPError as error:
            with error:
                return error.code, error.read().decode()

    try:
        with ThreadPoolExecutor(max_workers=1) as client:
            held = client.submit(get, '/hold')
            try:
                assert entered.wait(2), 'held request never entered worker'
                live = get('/live')
                rejected = get('/work')
                assert live == (200, 'process responding')
                assert rejected == (503, 'capacity unavailable; work not accepted')
                assert not held.done(), 'held request finished before capacity check'
            finally:
                release.set()
            assert held.result(timeout=3) == (200, 'work completed')
        recovered = get('/work')
        failed = get('/fail')
        after_failure = get('/work')
        assert recovered == after_failure == (200, 'work completed')
        assert failed == (500, 'work failed')
        return {'live_while_busy': live[0], 'rejected_while_busy': rejected[0],
                'after_release': recovered[0], 'injected_failure': failed[0],
                'after_failure': after_failure[0],
                'scope': 'controlled local overlap; no production load or AWS evidence'}
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive(), 'server did not stop'


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    print(json.dumps(run(), indent=2))
