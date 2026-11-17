"""Local negative control: an independent bearer link bypasses the review route.

This is a deliberately unsafe second HTTP endpoint over invented bytes. It is
not S3, a presigned URL, a CDN cache, authentication, or secure deletion.
"""

from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

from review_lab import initialize_review
from visitor_lab import request, running_server


@contextmanager
def shared_copy_server(copy):
    token = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            if self.path != '/shared/' + token:
                status, body = 404, b''
            elif copy['body'] is None:
                status, body = 410, b''
            else:
                status, body = 200, copy['body']
            self.send_response(status)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', '/shared/' + token
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        if thread.is_alive():
            raise RuntimeError('Shared-copy loopback server did not stop')


def anonymous_get(base, route):
    try:
        with urlopen(base + route, timeout=3) as response:
            return response.status, response.read()
    except HTTPError as error:
        with error:
            return error.code, error.read()


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-intake-direct-link-') as raw:
        directory = Path(raw)
        database = directory / 'intake.sqlite'
        initialize_review(database)
        body = b'Invented enrollment form for a local privacy drill'
        digest = hashlib.sha256(body).hexdigest()
        # Unsafe design: a second server gets an independent copy at upload time.
        copy = {'body': body}
        with running_server(database) as (app, keys), shared_copy_server(copy) as (raw_host, link):
            assert request(app, keys, 'alice', 'POST', '/objects/form-1', body)[0] == 201
            after_upload = {
                'owner_route': request(app, keys, 'alice', 'GET', '/objects/form-1')[0],
                'shared_link': anonymous_get(raw_host, link)[0],
                'wrong_link': anonymous_get(raw_host, '/shared/not-the-token')[0],
            }
            assert request(app, keys, 'scanner-1', 'POST', '/scan/form-1',
                           {'digest': digest, 'decision': 'pass'})[0] == 200
            after_scan = {
                'owner_route': request(app, keys, 'alice', 'GET', '/objects/form-1')[0],
                'shared_link': anonymous_get(raw_host, link)[0],
            }
            assert request(app, keys, 'reviewer-1', 'POST', '/review/form-1',
                           {'digest': digest, 'decision': 'approve'})[0] == 200
            approved_read = request(app, keys, 'alice', 'GET', '/objects/form-1')
            assert approved_read == (200, body)
            assert request(app, keys, 'alice', 'DELETE', '/objects/form-1')[0] == 204
            after_withdrawal = {
                'owner_route': request(app, keys, 'alice', 'GET', '/objects/form-1')[0],
                'shared_link': anonymous_get(raw_host, link)[0],
            }
            # Explicitly retire the independent copy; the app withdrawal did not.
            copy['body'] = None
            after_copy_retirement = anonymous_get(raw_host, link)[0]
    assert not directory.exists()
    return {
        'after_upload': after_upload,
        'after_scan': after_scan,
        'approved_owner_read': approved_read[0],
        'after_withdrawal': after_withdrawal,
        'after_copy_retirement': after_copy_retirement,
        'temporary_resources_removed': True,
        'scope': 'Two loopback HTTP servers, invented bytes and temporary SQLite; '
                 'the shared copy deliberately ignores review state; no AWS, '
                 'presigned-URL semantics, real identity, cache or physical-erasure claim',
    }


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without -O; assertions are the lab checks')
    print(json.dumps(run(), indent=2))
