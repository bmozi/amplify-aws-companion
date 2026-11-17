"""Loopback HTTP contract drill with SQLite transactions and public fixture tokens.

Not a production server, identity provider, API Gateway emulator or AWS deployment.
"""
from concurrent.futures import ThreadPoolExecutor
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import uuid

# Public teaching fixtures, never real credentials. No JWT validation or TLS here.
USERS = {'Bearer fixture-alice': 'alice', 'Bearer fixture-bob': 'bob'}


def connect(path):
    return sqlite3.connect(path, timeout=5)


def handler_for(path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, body):
            data = json.dumps(body).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def caller(self):
            caller = USERS.get(self.headers.get('Authorization'))
            if caller is None:
                self.reply(401, {'error': 'fixture_identity_required'})
            return caller

        def do_POST(self):
            caller = self.caller()
            if caller is None:
                return
            if self.path != '/repairs':
                return self.reply(404, {'error': 'not_found'})
            key = self.headers.get('Idempotency-Key', '')
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1024 or not 0 < len(key) <= 80:
                    raise ValueError('invalid envelope')
                body = json.loads(self.rfile.read(length))
                if (not isinstance(body, dict) or set(body) != {'repair'}
                        or not isinstance(body['repair'], str)
                        or not body['repair'].strip() or len(body['repair']) > 200):
                    raise ValueError('invalid repair')
            except (ValueError, UnicodeError):
                return self.reply(400, {'error': 'invalid_request'})
            intent = json.dumps(body, sort_keys=True)
            # One connection per request; BEGIN IMMEDIATE serializes conflicting writers.
            # Both the request and work obligation commit together, before any receipt.
            db = connect(path)
            try:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute('SELECT id, intent, state FROM requests WHERE owner=? AND retry_key=?',
                                 (caller, key)).fetchone()
                if row and row[1] != intent:
                    db.rollback()
                    return self.reply(409, {'error': 'retry_conflict'})
                if row:
                    request_id, _, state = row
                    response_code = 200
                else:
                    request_id, state = uuid.uuid4().hex, 'accepted'
                    response_code = 202
                    db.execute('INSERT INTO requests VALUES (?, ?, ?, ?, ?)',
                               (request_id, caller, key, intent, state))
                    # Local fault injection, deliberately NOT a production API feature.
                    if self.headers.get('X-Fixture-Fault') == 'before-obligation':
                        db.rollback()
                        return self.reply(503, {'error': 'acceptance_failed'})
                    db.execute('INSERT INTO obligations VALUES (?)', (request_id,))
                db.commit()
            finally:
                db.close()
            if self.headers.get('X-Fixture-Fault') == 'lose-reply':
                self.close_connection = True  # Commit succeeded; return no HTTP response.
                return
            self.reply(response_code, {'request_id': request_id, 'state': state,
                             'status_url': '/repairs/' + request_id})

        def do_GET(self):
            caller = self.caller()
            if caller is None:
                return
            request_id = self.path.removeprefix('/repairs/')
            db = connect(path)
            try:
                row = db.execute('SELECT state FROM requests WHERE id=? AND owner=?',
                                 (request_id, caller)).fetchone() if self.path.startswith('/repairs/') else None
            finally:
                db.close()
            if row is None:
                return self.reply(404, {'error': 'not_found'})
            self.reply(200, {'request_id': request_id, 'state': row[0]})
    return Handler


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-api-contract-') as directory:
        path = Path(directory) / 'requests.sqlite'
        db = connect(path)
        db.executescript('''CREATE TABLE requests (
          id TEXT PRIMARY KEY, owner TEXT NOT NULL, retry_key TEXT NOT NULL,
          intent TEXT NOT NULL, state TEXT NOT NULL, UNIQUE(owner, retry_key));
          CREATE TABLE obligations (request_id TEXT PRIMARY KEY);''')
        db.close()
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(path))
        server.timeout = 5
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(method, route='/repairs', key='original', repair='repair chair',
                    token='fixture-alice', fault=None):
            client = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=5)
            headers = {'Authorization': 'Bearer ' + token, 'Idempotency-Key': key}
            if fault:
                headers['X-Fixture-Fault'] = fault
            try:
                client.request(method, route, json.dumps({'repair': repair}) if method == 'POST' else None, headers)
                response = client.getresponse()
                return response.status, json.loads(response.read())
            finally:
                client.close()

        def counts():
            db = connect(path)
            try:
                return tuple(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
                             for table in ('requests', 'obligations'))
            finally:
                db.close()

        try:
            assert request('POST', token='unknown')[0] == 401
            assert request('POST', repair='')[0] == 400
            assert counts() == (0, 0)
            assert request('POST', fault='before-obligation')[0] == 503
            assert counts() == (0, 0), 'No half-accepted request may survive rollback'
            print('Invalid/unauthorized input and injected storage failure: no accepted work')

            try:
                request('POST', fault='lose-reply')
            except http.client.RemoteDisconnected:
                pass
            else:
                raise AssertionError('Expected committed acceptance with a missing HTTP reply')
            assert counts() == (1, 1)
            status, receipt = request('POST')
            assert status == 200 and receipt['state'] == 'accepted' and counts() == (1, 1)
            assert request('POST', repair='different repair')[0] == 409
            assert counts() == (1, 1)
            print('Lost reply: original key recovers one stored request; changed intent conflicts')

            route = receipt['status_url']
            assert request('GET', route)[0] == 200
            assert request('GET', route, token='fixture-bob') == (404, {'error': 'not_found'})
            assert request('GET', route, token='unknown')[0] == 401
            # Same public key in a different trusted caller scope means separate work.
            assert request('POST', token='fixture-bob')[1]['request_id'] != receipt['request_id']
            assert counts() == (2, 2)
            print('Owner can read status; adjacent customer cannot; keys are caller-scoped')

            with ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda _: request('POST', key='concurrent'), range(6)))
            assert sorted(code for code, _ in results) == [200, 200, 200, 200, 200, 202]
            assert len({body['request_id'] for _, body in results}) == 1
            assert counts() == (3, 3)
            print('Six concurrent HTTP retries: one request and one work obligation')

            # A local operator records a fictional business rejection; no external repair occurs.
            db = connect(path)
            with db:
                db.execute('UPDATE requests SET state=? WHERE id=?', ('rejected', receipt['request_id']))
            db.close()
            assert request('GET', route) == (200, {'request_id': receipt['request_id'], 'state': 'rejected'})
            assert request('POST')[1]['state'] == 'rejected'
            print('HTTP 200 status lookup truthfully reports business rejection')

            # Negative control: changing the key creates another operation for the same intent.
            assert request('POST', key='fresh-key')[0] == 202
            assert counts() == (4, 4)
            print('Unsafe fresh key: another request is accepted for the same repair text')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            assert not thread.is_alive()
    assert not Path(directory).exists()
    print('PASS: loopback listener closed and temporary database removed; no AWS calls')


if __name__ == '__main__':
    if __debug__ is False:
        raise SystemExit('Run without -O; assertions are the exercise checks')
    run()
