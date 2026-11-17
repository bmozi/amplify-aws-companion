"""Two local HTTP clients exercise owner checks and a SQLite revision condition."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import sqlite3
import tempfile
from threading import Barrier, Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from lab import apply_update


def make_handler():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def answer(self, status, data):
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            if status == 200 and 'revision' in data:
                self.send_header('ETag', f'"{data["revision"]}"')
            self.end_headers()
            self.wfile.write(body)

        def actor(self):
            header = self.headers.get('Authorization', '')
            if not header.startswith('Bearer '):
                return None
            supplied = header[7:]
            for token, name in self.server.tokens.items():
                if secrets.compare_digest(supplied, token):
                    return name
            return None

        def authorized_record(self):
            actor = self.actor()
            if actor is None:
                self.answer(401, {'error': 'missing_or_invalid_token'})
                return None
            if self.path != '/parts/0012':
                self.answer(404, {'error': 'unknown_path'})
                return None
            with sqlite3.connect(self.server.database, timeout=5) as db:
                row = db.execute('SELECT part_id, owner, price_cents, note, revision '
                                 'FROM parts WHERE part_id = ?', ('0012',)).fetchone()
            if row is None:
                self.answer(404, {'error': 'missing_part'})
                return None
            part_id, owner, price, note, revision = row
            if actor != owner:
                self.answer(403, {'error': 'not_owner'})
                return None
            return {'part_id': part_id, 'price_cents': price, 'note': note,
                    'revision': revision}

        def do_GET(self):
            record = self.authorized_record()
            if record is not None:
                self.answer(200, record)

        def do_PUT(self):
            record = self.authorized_record()
            if record is None:
                return
            supplied_revision = self.headers.get('If-Match')
            if supplied_revision is None:
                self.answer(428, {'error': 'etag_required'})
                return
            if not re.fullmatch(r'"[1-9][0-9]*"', supplied_revision):
                self.answer(400, {'error': 'single_strong_etag_required'})
                return
            # The proposed copy below is built from this read. A future tag
            # must not become valid after another writer advances the row.
            if int(supplied_revision[1:-1]) != record['revision']:
                self.answer(412, {'error': 'etag_mismatch'})
                return
            size = self.headers.get('Content-Length', '')
            if not size.isdecimal() or not 0 < int(size) <= 1024:
                self.answer(400, {'error': 'invalid_body_size'})
                return
            try:
                proposed = apply_update(record, self.rfile.read(int(size)))
            except ValueError:
                self.answer(400, {'error': 'invalid_update'})
                return
            if self.headers.get('X-Lab-Race') == 'yes':
                self.server.race.wait(timeout=5)
            with sqlite3.connect(self.server.database, timeout=5) as db:
                changed = db.execute(
                    'UPDATE parts SET price_cents = ?, note = ?, revision = revision + 1 '
                    'WHERE part_id = ? AND owner = ? AND revision = ?',
                    (proposed['price_cents'], proposed['note'], '0012', self.actor(),
                     int(supplied_revision[1:-1])),
                ).rowcount
                if changed == 1:
                    row = db.execute('SELECT price_cents, note, revision FROM parts '
                                     'WHERE part_id = ?', ('0012',)).fetchone()
            if changed == 0:
                self.answer(412, {'error': 'etag_mismatch'})
            else:
                self.answer(200, {'part_id': '0012', 'price_cents': row[0],
                                  'note': row[1], 'revision': row[2]})
    return Handler


def request(base, method, token=None, revision=None, update=None, race=False):
    headers = {}
    if token is not None:
        headers['Authorization'] = 'Bearer ' + token
    if revision is not None:
        headers['If-Match'] = revision if isinstance(revision, str) else f'"{revision}"'
    if race:
        headers['X-Lab-Race'] = 'yes'
    data = json.dumps(update).encode() if update is not None else None
    if data is not None:
        headers['Content-Type'] = 'application/json'
    outgoing = Request(base + '/parts/0012', data=data, headers=headers, method=method)
    try:
        with urlopen(outgoing, timeout=8) as response:
            return response.status, json.load(response), response.headers.get('ETag')
    except HTTPError as error:
        with error:
            return error.code, json.load(error), error.headers.get('ETag')


def run():
    with tempfile.TemporaryDirectory() as folder:
        database = Path(folder) / 'parts.sqlite'
        with sqlite3.connect(database) as db:
            db.execute('CREATE TABLE parts (part_id TEXT PRIMARY KEY, owner TEXT NOT NULL, '
                       'price_cents INTEGER NOT NULL, note TEXT, revision INTEGER NOT NULL)')
            db.execute('INSERT INTO parts VALUES (?, ?, ?, ?, ?)',
                       ('0012', 'maya', 30, 'Keep dry', 1))
        owner_token = secrets.token_urlsafe(24)
        other_token = secrets.token_urlsafe(24)
        server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler())
        server.database = database
        server.tokens = {owner_token: 'maya', other_token: 'lee'}
        server.race = Barrier(2)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            assert request(base, 'GET')[0] == 401
            assert request(base, 'GET', other_token)[0] == 403
            assert request(base, 'PUT', other_token, 1,
                           {'version': 1, 'part_id': '0012', 'price_cents': 99})[0] == 403
            original_status, original, original_etag = request(base, 'GET', owner_token)
            assert original_status == 200 and original['revision'] == 1
            assert original_etag == '"1"'
            assert request(base, 'PUT', owner_token, update={'version': 1,
                           'part_id': '0012', 'price_cents': 45})[0] == 428
            assert request(base, 'PUT', owner_token, 'W/"1"', {'version': 1,
                           'part_id': '0012', 'price_cents': 45})[0] == 400
            assert request(base, 'PUT', owner_token, 1, {'version': 1,
                           'part_id': '0012', 'price_cents': True})[0] == 400
            class AdvanceAtUpdate:
                def wait(self, timeout):
                    with sqlite3.connect(database) as db:
                        db.execute('UPDATE parts SET price_cents = 88, revision = 2 '
                                   'WHERE part_id = ?', ('0012',))

            # The hook represents a concurrent write after the initial read.
            # A future tag must be rejected before that stale copy can be used.
            server.race = AdvanceAtUpdate()
            assert request(base, 'PUT', owner_token, 2, {'version': 1,
                           'part_id': '0012', 'note': 'Future tag'}, True)[0] == 412
            assert request(base, 'GET', owner_token)[1] == original
            server.race = Barrier(2)
            price = {'version': 1, 'part_id': '0012', 'price_cents': 45}
            note = {'version': 1, 'part_id': '0012', 'note': 'Inspect seal'}
            with ThreadPoolExecutor(max_workers=2) as pool:
                left = pool.submit(request, base, 'PUT', owner_token, original_etag, price, True)
                right = pool.submit(request, base, 'PUT', owner_token, original_etag, note, True)
                competing = [left.result(), right.result()]
            assert sorted(status for status, _, _ in competing) == [200, 412]
            fresh_status, fresh, fresh_etag = request(base, 'GET', owner_token)
            assert fresh_status == 200 and fresh['revision'] == 2 and fresh_etag == '"2"'
            missing_change = note if fresh['price_cents'] == 45 else price
            merged_status, merged, merged_etag = request(base, 'PUT', owner_token, fresh_etag, missing_change)
            assert merged_status == 200 and merged_etag == '"3"'
            assert merged == {'part_id': '0012', 'price_cents': 45,
                              'note': 'Inspect seal', 'revision': 3}
            assert request(base, 'PUT', owner_token, original_etag, price)[0] == 412
            assert request(base, 'GET', other_token)[0] == 403
            print(json.dumps({
                'missing_token': 401, 'other_owner': 403, 'missing_etag': 428,
                'weak_etag': 400, 'invalid_price': 400,
                'future_etag': 412,
                'competing_updates': sorted(s for s, _, _ in competing),
                'reviewed_merge': merged, 'replayed_stale_update': 412,
                'scope': 'Loopback HTTP, fixture bearer tokens and local SQLite only; no AWS identity or cloud concurrency',
            }))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == '__main__':
    run()
