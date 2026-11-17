"""Loopback-only A04 visitor path over the existing synthetic two-gate SQLite rules."""

from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from lab import delete, read, upload
from review_lab import decide, initialize_review


def server_for(path, tokens):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def actor(self):
            header = self.headers.get('Authorization', '')
            if not header.startswith('Bearer '):
                return None
            return tokens.get(header[7:])

        def object_id(self, prefix):
            if not self.path.startswith(prefix):
                return None
            value = self.path[len(prefix):]
            if not value or len(value) > 40 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in value):
                return None
            return value

        def respond(self, status, payload=b'', content_type='application/json'):
            if isinstance(payload, dict):
                payload = json.dumps(payload, sort_keys=True).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)

        def input(self, maximum):
            raw = self.headers.get('Content-Length', '')
            if not raw.isdigit() or not 0 < int(raw) <= maximum:
                raise ValueError('Missing or excessive request body')
            body = self.rfile.read(int(raw))
            if len(body) != int(raw):
                raise ValueError('Incomplete request body')
            return body

        def do_GET(self):
            actor = self.actor()
            if actor is None:
                return self.respond(403, {'error': 'No fixture identity'})
            object_id = self.object_id('/objects/')
            if object_id is None:
                return self.respond(404, {'error': 'No route'})
            try:
                body = read(path, object_id, actor)
            except PermissionError:
                return self.respond(404, {'error': 'Not available'})
            self.respond(200, body, 'application/octet-stream')

        def do_POST(self):
            actor = self.actor()
            if actor is None:
                return self.respond(403, {'error': 'No fixture identity'})
            object_id = self.object_id('/objects/')
            if object_id is not None:
                if actor != 'alice':
                    return self.respond(403, {'error': 'Only fixture owner may upload'})
                try:
                    digest = upload(path, object_id, actor, self.input(1024))
                except ValueError as error:
                    return self.respond(409, {'error': str(error)})
                return self.respond(201, {'object_id': object_id, 'digest': digest, 'state': 'quarantined'})
            gate = 'scan' if self.object_id('/scan/') else 'review' if self.object_id('/review/') else None
            object_id = self.object_id('/scan/') or self.object_id('/review/')
            if gate is None:
                return self.respond(404, {'error': 'No route'})
            try:
                packet = json.loads(self.input(4096))
                if not isinstance(packet, dict):
                    raise ValueError('Decision packet must be an object')
                result = decide(path, object_id, packet.get('digest'), actor, gate, packet.get('decision'))
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
                return self.respond(409, {'error': str(error)})
            except PermissionError:
                return self.respond(403, {'error': 'Actor lacks this gate'})
            return self.respond(200, {'state': result})

        def do_DELETE(self):
            actor = self.actor()
            if actor is None:
                return self.respond(403, {'error': 'No fixture identity'})
            object_id = self.object_id('/objects/')
            if object_id is None:
                return self.respond(404, {'error': 'No route'})
            try:
                delete(path, object_id, actor)
            except PermissionError:
                return self.respond(404, {'error': 'Not available'})
            self.respond(204, b'')

    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)


@contextmanager
def running_server(path):
    tokens = {secrets.token_urlsafe(24): actor for actor in
              ('alice', 'bob', 'scanner-1', 'reviewer-1')}
    keys = {actor: token for token, actor in tokens.items()}
    server = server_for(path, tokens)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', keys
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def request(base, keys, actor, method, route, body=None):
    headers = {'Authorization': 'Bearer ' + keys[actor]}
    if isinstance(body, dict):
        body = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    call = Request(base + route, data=body, headers=headers, method=method)
    try:
        with urlopen(call, timeout=3) as reply:
            return reply.status, reply.read()
    except HTTPError as error:
        return error.code, error.read()


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-intake-http-') as raw:
        directory = Path(raw)
        path = directory / 'intake.sqlite'
        initialize_review(path)
        with running_server(path) as (base, keys):
            body = b'Invented enrollment form'
            digest = hashlib.sha256(body).hexdigest()
            status, receipt = request(base, keys, 'alice', 'POST', '/objects/form-1', body)
            assert status == 201 and json.loads(receipt)['digest'] == digest
            assert request(base, keys, 'alice', 'GET', '/objects/form-1')[0] == 404
            assert request(base, keys, 'alice', 'GET', '/raw/form-1')[0] == 404
            assert request(base, keys, 'reviewer-1', 'POST', '/review/form-1',
                           {'digest': digest, 'decision': 'approve'})[0] == 409
            assert request(base, keys, 'alice', 'POST', '/review/form-1',
                           {'digest': digest, 'decision': 'approve', 'actor': 'reviewer-1'})[0] == 403
            assert request(base, keys, 'scanner-1', 'POST', '/scan/form-1',
                           {'digest': digest, 'decision': 'pass'})[0] == 200
            assert request(base, keys, 'alice', 'GET', '/objects/form-1')[0] == 404
            assert request(base, keys, 'reviewer-1', 'POST', '/review/form-1',
                           {'digest': 'wrong', 'decision': 'approve'})[0] == 409
            assert request(base, keys, 'reviewer-1', 'POST', '/review/form-1',
                           {'digest': digest, 'decision': 'approve'})[0] == 200
            assert request(base, keys, 'alice', 'GET', '/objects/form-1') == (200, body)
            assert request(base, keys, 'bob', 'GET', '/objects/form-1')[0] == 404
            assert request(base, keys, 'scanner-1', 'GET', '/objects/form-1')[0] == 404
            assert request(base, keys, 'alice', 'GET', '/raw/form-1')[0] == 404
            assert request(base, keys, 'alice', 'DELETE', '/objects/form-1')[0] == 204
            assert request(base, keys, 'alice', 'GET', '/objects/form-1')[0] == 404
            assert request(base, keys, 'reviewer-1', 'POST', '/review/form-1',
                           {'digest': digest, 'decision': 'approve'})[1] == b'{"state": "ignored_deleted"}'
            rejected = b'Invented rejected form'
            bad_digest = hashlib.sha256(rejected).hexdigest()
            assert request(base, keys, 'alice', 'POST', '/objects/form-2', rejected)[0] == 201
            assert request(base, keys, 'scanner-1', 'POST', '/scan/form-2',
                           {'digest': bad_digest, 'decision': 'fail'})[0] == 200
            assert request(base, keys, 'alice', 'GET', '/objects/form-2')[0] == 404
    assert not directory.exists()
    return {'upload_quarantined': True, 'scan_alone_private': True,
            'reviewer_body_spoof_denied': True, 'wrong_digest_denied': True,
            'owner_read_after_both_gates': True, 'other_owner_denied': True,
            'withdrawal_closes_route': True, 'rejected_file_private': True,
            'temporary_resources_removed': True,
            'scope': 'Loopback HTTP plus local SQLite and ephemeral fixture bearer tokens; no real authentication, scanner, S3 policy, callback or AWS deployment'}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without -O; assertions are the lab checks')
    print(json.dumps(run(), indent=2))
