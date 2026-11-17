"""Integrated local pickup journey; synthetic actors, clock and stock, no AWS."""

from contextlib import contextmanager
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import sqlite3
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


REQUEST_PATH = re.compile(r"^/requests/(r-[0-9a-f]{32})(/label)?$")
INVENTORY_PATH = re.compile(r"^/inventory/(r-[0-9a-f]{32})/(confirm|ready)$")


def connect(path):
    return sqlite3.connect(path, timeout=3)


class Pickup:
    def __init__(self, path):
        self.path = Path(path)
        with connect(path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY, partner TEXT NOT NULL, retry_key TEXT NOT NULL,
                    depot TEXT NOT NULL, item TEXT NOT NULL, status TEXT NOT NULL,
                    accepted_min INTEGER NOT NULL, due_min INTEGER NOT NULL,
                    confirmed_min INTEGER, ready_min INTEGER,
                    UNIQUE(partner, retry_key)
                );
                CREATE TABLE IF NOT EXISTS inventory (depot TEXT PRIMARY KEY, available INTEGER NOT NULL
                    CHECK(available >= 0));
                INSERT OR IGNORE INTO inventory VALUES ('depot-1', 1);
            """)

    def submit(self, partner, key, depot, item, minute):
        if (partner not in ('partner-a', 'partner-b') or not isinstance(key, str)
                or not re.fullmatch(r'[A-Za-z0-9-]{1,40}', key)
                or type(minute) is not int or minute < 0):
            raise ValueError('Invalid pickup request')
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT id,depot,item FROM requests WHERE partner=? AND retry_key=?',
                                  (partner, key)).fetchone()
            if existing:
                if existing[1:] != (depot, item):
                    raise ValueError('Retry key has different intent')
                return {'id': existing[0], 'replayed': True,
                        'status': self._row(db, existing[0])['status']}
            if depot != 'depot-1' or item != 'food_box':
                raise ValueError('Invalid pickup request')
            request_id = 'r-' + uuid4().hex
            db.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (request_id, partner, key, depot, item, 'pending_inventory',
                        minute, minute + 90, None, None))
            return {'id': request_id, 'replayed': False, 'status': 'pending_inventory'}

    @staticmethod
    def _row(db, request_id):
        db.row_factory = sqlite3.Row
        row = db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
        return dict(row) if row else None

    def status(self, partner, request_id):
        with connect(self.path) as db:
            row = self._row(db, request_id)
        if not row or row['partner'] != partner:
            raise PermissionError('Request unavailable')
        return {'id': row['id'], 'status': row['status'], 'accepted_min': row['accepted_min'],
                'due_min': row['due_min'], 'confirmed_min': row['confirmed_min'],
                'ready_min': row['ready_min'],
                'ready_on_time': (row['ready_min'] <= row['due_min']
                                  if row['ready_min'] is not None else None)}

    def label(self, partner, request_id):
        result = self.status(partner, request_id)
        if result['status'] != 'ready':
            raise PermissionError('Label unavailable')
        return f"Synthetic pickup label for {request_id}".encode()

    def confirm(self, operator, request_id, minute):
        if type(minute) is not int or minute < 0:
            raise ValueError('Invalid fixture clock')
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._row(db, request_id)
            if not row or operator != 'operator-depot-1' or row['depot'] != 'depot-1':
                raise PermissionError('Depot decision unavailable')
            if row['status'] != 'pending_inventory':
                return row['status']
            if minute < row['accepted_min']:
                raise ValueError('Confirmation time precedes acceptance')
            available = db.execute('SELECT available FROM inventory WHERE depot=?',
                                   (row['depot'],)).fetchone()[0]
            if available == 0:
                db.execute("UPDATE requests SET status='unavailable',confirmed_min=? WHERE id=?",
                           (minute, request_id))
                return 'unavailable'
            db.execute('UPDATE inventory SET available=available-1 WHERE depot=?', (row['depot'],))
            db.execute("UPDATE requests SET status='reserved',confirmed_min=? WHERE id=?",
                       (minute, request_id))
            return 'reserved'

    def ready(self, operator, request_id, minute):
        if type(minute) is not int or minute < 0:
            raise ValueError('Invalid fixture clock')
        with connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._row(db, request_id)
            if not row or operator != 'operator-depot-1' or row['depot'] != 'depot-1':
                raise PermissionError('Depot decision unavailable')
            if row['status'] == 'ready':
                return row['ready_min'] <= row['due_min']
            if row['status'] != 'reserved':
                raise ValueError('Inventory has not been reserved')
            if minute < row['confirmed_min']:
                raise ValueError('Ready time precedes stock confirmation')
            db.execute("UPDATE requests SET status='ready',ready_min=? WHERE id=?",
                       (minute, request_id))
            return minute <= row['due_min']

    def stock(self):
        with connect(self.path) as db:
            return db.execute("SELECT available FROM inventory WHERE depot='depot-1'").fetchone()[0]


def handler_for(service, tokens, clock):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def actor(self):
            header = self.headers.get('Authorization', '')
            return tokens.get(header[7:]) if header.startswith('Bearer ') else None

        def answer(self, status, payload):
            raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/octet-stream' if isinstance(payload, bytes)
                             else 'application/json')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def body(self):
            size = self.headers.get('Content-Length', '')
            if not size.isdigit() or not 0 < int(size) <= 512:
                raise ValueError('Invalid request size')
            packet = json.loads(self.rfile.read(int(size)))
            if not isinstance(packet, dict):
                raise ValueError('Invalid request body')
            return packet

        def do_POST(self):
            actor = self.actor()
            if actor is None:
                return self.answer(403, {'error': 'No fixture identity'})
            if self.path == '/requests':
                if actor not in ('partner-a', 'partner-b'):
                    return self.answer(403, {'error': 'Partner required'})
                try:
                    packet = self.body()
                    receipt = service.submit(actor, packet.get('retry_key'), packet.get('depot'),
                                             packet.get('item'), clock['minute'])
                except (ValueError, json.JSONDecodeError):
                    return self.answer(409, {'error': 'Invalid or changed request'})
                if self.headers.get('X-Simulate-Reply-Loss') == 'yes':
                    self.close_connection = True  # commit occurred; client sees no receipt
                    return
                return self.answer(200 if receipt['replayed'] else 201, receipt)
            match = INVENTORY_PATH.fullmatch(self.path)
            if not match:
                return self.answer(404, {'error': 'No route'})
            try:
                if match.group(2) == 'confirm':
                    result = {'status': service.confirm(actor, match.group(1), clock['minute'])}
                else:
                    on_time = service.ready(actor, match.group(1), clock['minute'])
                    result = {'status': 'ready', 'on_time': on_time}
            except PermissionError:
                return self.answer(403, {'error': 'Depot authority required'})
            except ValueError as error:
                return self.answer(409, {'error': str(error)})
            return self.answer(200, result)

        def do_GET(self):
            actor = self.actor()
            if actor not in ('partner-a', 'partner-b'):
                return self.answer(403, {'error': 'Partner required'})
            match = REQUEST_PATH.fullmatch(self.path)
            if not match:
                return self.answer(404, {'error': 'No route'})
            try:
                result = (service.label(actor, match.group(1)) if match.group(2)
                          else service.status(actor, match.group(1)))
            except PermissionError:
                return self.answer(404, {'error': 'Request unavailable'})
            return self.answer(200, result)

    return Handler


@contextmanager
def serve(service, clock):
    tokens = {secrets.token_urlsafe(24): actor for actor in
              ('partner-a', 'partner-b', 'operator-depot-1')}
    keys = {actor: token for token, actor in tokens.items()}
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(service, tokens, clock))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}', keys
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        if thread.is_alive():
            raise RuntimeError('Pickup loopback server did not stop')


def call(base, keys, actor, method, route, packet=None, lose_reply=False):
    data = None if packet is None else json.dumps(packet).encode()
    headers = {'Authorization': 'Bearer ' + keys[actor]}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    if lose_reply:
        headers['X-Simulate-Reply-Loss'] = 'yes'
    request = Request(base + route, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=3) as response:
            raw = response.read()
            return response.status, raw if route.endswith('/label') else json.loads(raw)
    except HTTPError as error:
        with error:
            return error.code, json.loads(error.read())
    except RemoteDisconnected:
        return None, {'error': 'reply lost after local commit'}


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-food-bank-') as raw:
        folder = Path(raw)
        database = folder / 'pickup.sqlite'
        service = Pickup(database)
        clock = {'minute': 0}
        intent = {'retry_key': 'morning-1', 'depot': 'depot-1', 'item': 'food_box'}
        with serve(service, clock) as (base, keys):
            lost = call(base, keys, 'partner-a', 'POST', '/requests', intent, lose_reply=True)
        with connect(database) as db:
            committed_id = db.execute(
                "SELECT id FROM requests WHERE partner='partner-a' AND retry_key='morning-1'"
            ).fetchone()[0]
        service = Pickup(database)  # new service object and HTTP server; committed request survives
        with serve(service, clock) as (base, keys):
            replay_status, replay = call(base, keys, 'partner-a', 'POST', '/requests', intent)
            request_id = replay['id']
            pending = call(base, keys, 'partner-a', 'GET', '/requests/' + request_id)
            neighbor = call(base, keys, 'partner-b', 'GET', '/requests/' + request_id)
            early_label = call(base, keys, 'partner-a', 'GET', '/requests/' + request_id + '/label')
            partner_cannot_allocate = call(base, keys, 'partner-a', 'POST',
                                           '/inventory/' + request_id + '/confirm')
            clock['minute'] = 30
            confirmed = call(base, keys, 'operator-depot-1', 'POST',
                             '/inventory/' + request_id + '/confirm')
            clock['minute'] = 20  # negative control: a backdated ready event cannot rewrite order
            backdated = call(base, keys, 'operator-depot-1', 'POST',
                             '/inventory/' + request_id + '/ready')
            clock['minute'] = 75
            ready = call(base, keys, 'operator-depot-1', 'POST',
                         '/inventory/' + request_id + '/ready')
            final = call(base, keys, 'partner-a', 'GET', '/requests/' + request_id)
            label = call(base, keys, 'partner-a', 'GET', '/requests/' + request_id + '/label')
            neighbor_label = call(base, keys, 'partner-b', 'GET', '/requests/' + request_id + '/label')
            second_status, second = call(base, keys, 'partner-b', 'POST', '/requests', intent)
            no_stock = call(base, keys, 'operator-depot-1', 'POST',
                            '/inventory/' + second['id'] + '/confirm')
            assert (lost[0] is None and replay_status == 200 and replay['replayed']
                    and request_id == committed_id
                    and pending[1]['status'] == 'pending_inventory' and neighbor[0] == 404
                    and early_label[0] == 404 and partner_cannot_allocate[0] == 403
                    and confirmed[1]['status'] == 'reserved' and backdated[0] == 409
                    and ready[1]['on_time']
                    and final[1]['status'] == 'ready' and final[1]['confirmed_min'] == 30
                    and final[1]['ready_min'] == 75 and label[0] == 200
                    and neighbor_label[0] == 404 and second_status == 201
                    and no_stock[1]['status'] == 'unavailable' and service.stock() == 0)
    assert not folder.exists()
    return {'lost_reply': lost, 'replay_status': replay_status, 'same_intent_replayed': replay['replayed'],
            'recovered_committed_id_after_restart': request_id == committed_id,
            'pending_before_inventory': pending[1]['status'], 'neighbor_read_status': neighbor[0],
            'early_label_status': early_label[0], 'partner_allocate_status': partner_cannot_allocate[0],
            'confirmed_status': confirmed[1]['status'], 'ready_on_time_at_minute_75': ready[1]['on_time'],
            'backdated_ready_status': backdated[0],
            'confirmed_min': final[1]['confirmed_min'], 'ready_min': final[1]['ready_min'],
            'final_status': final[1]['status'], 'owner_label_status': label[0],
            'neighbor_label_status': neighbor_label[0], 'same_key_other_partner_status': second_status,
            'second_request_no_stock': no_stock[1]['status'], 'remaining_stock': 0,
            'temporary_files_removed': True,
            'scope': 'Same-machine loopback HTTP restart and SQLite, fixture bearer identities/clock/inventory; '
                     'no AWS, real partners, external inventory, attachment storage, measured capacity or '
                     '90-minute service guarantee'}


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without -O; assertions are the lab checks')
    print(json.dumps(run(), indent=2))
