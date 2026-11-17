"""Loopback cache negative control for a withdrawn synthetic media revision.

This deliberately uses a cacheable origin response in one path. It is not a
CloudFront, browser, S3, invalidation, or global propagation test.
"""

from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

from lab import digest, publish
from read_path import visitor_server, withdraw


def request(url):
    try:
        with urlopen(url, timeout=3) as response:
            return response.status, response.read(), dict(response.headers)
    except HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def cache_server(origin, clock):
    """Cache only explicit /media/ requests with a positive max-age."""
    entries = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = self.path
            if not path.startswith('/media/') or '?' in path or '#' in path:
                self.send_error(404)
                return
            cached = entries.get(path)
            if cached and clock[0] < cached[0]:
                self.reply(200, cached[1], 'HIT')
                return
            status, body, headers = request(origin + path)
            control = headers.get('Cache-Control', '')
            if status == 200 and control.startswith('public, max-age='):
                lifetime = int(control.removeprefix('public, max-age='))
                if lifetime > 0:
                    entries[path] = (clock[0] + lifetime, body)
            else:
                entries.pop(path, None)
            self.reply(status, body, 'MISS')

        def reply(self, status, body, cache_state):
            self.send_response(status)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('X-Lab-Cache', cache_state)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)


def run():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    objects = {'private/original': b'fictional museum original'}
    variants = {}
    for name in ('thumbnail', 'large'):
        key = f'published/8/{name}'
        value = f'synthetic approved {name} bytes'.encode()
        objects[key] = value
        variants[name] = {'key': key, 'digest': digest(value)}
    manifest = {'revision': 8, 'source_digest': digest(objects['private/original']),
                'recipe': 'synthetic-v1', 'variants': variants}
    approval = digest(json.dumps(manifest, sort_keys=True).encode())
    clock = [0]

    with tempfile.TemporaryDirectory(prefix='amplify-media-cache-') as folder:
        db_path = Path(folder) / 'publication.sqlite'
        with closing(sqlite3.connect(db_path, isolation_level=None)) as db:
            db.execute('CREATE TABLE current (generation INTEGER, revision INTEGER, manifest TEXT)')
            db.execute("INSERT INTO current VALUES (0,0,'{}')")
            assert publish(db, objects, manifest, approval, 0) == 'published'
            # The ordinary reader lab uses no-store. The second origin changes
            # only its response header to expose a deliberately cached path.
            plain = visitor_server(db_path, objects)
            cacheable = visitor_server(db_path, objects, 'public, max-age=60')
            plain_proxy = cache_server(f'http://127.0.0.1:{plain.server_port}', clock)
            stale_proxy = cache_server(f'http://127.0.0.1:{cacheable.server_port}', clock)
            servers = (plain, cacheable, plain_proxy, stale_proxy)
            workers = [threading.Thread(target=server.serve_forever) for server in servers]
            for worker in workers:
                worker.start()
            try:
                path = '/media/8/large'
                direct = f'http://127.0.0.1:{plain.server_port}'
                safe = f'http://127.0.0.1:{plain_proxy.server_port}'
                stale = f'http://127.0.0.1:{stale_proxy.server_port}'
                expected = objects['published/8/large']
                assert request(safe + path)[:2] == (200, expected)
                assert request(stale + path)[:2] == (200, expected)
                assert request(stale + path)[2]['X-Lab-Cache'] == 'HIT'
                saved_copy = expected
                assert request(direct + '/private/original')[0] == 404

                assert withdraw(db, 1) == 'withdrawn'
                assert request(direct + '/current')[0] == 410
                assert request(direct + path)[0] == 404
                safe_result = request(safe + path)
                assert safe_result[0] == 404 and safe_result[2]['X-Lab-Cache'] == 'MISS'
                stale_result = request(stale + path)
                assert stale_result[:2] == (200, expected)
                assert stale_result[2]['X-Lab-Cache'] == 'HIT'
                clock[0] = 61
                expired = request(stale + path)
                assert expired[0] == 404 and expired[2]['X-Lab-Cache'] == 'MISS'
                assert saved_copy == expected
                print('PASS: after withdrawal, origin 404 and no-store proxy MISS 404;')
                print('cacheable proxy HIT 200 until its simulated 60-second expiry;')
                print('the already saved byte copy remains after proxy expiry.')
                print('No real browser cache, CloudFront, S3, propagation or revocation proof.')
            finally:
                for server in servers:
                    server.shutdown()
                for worker in workers:
                    worker.join(timeout=3)
                    assert not worker.is_alive()
                for server in servers:
                    server.server_close()


if __name__ == '__main__':
    run()
