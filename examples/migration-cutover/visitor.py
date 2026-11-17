"""Follow a fictional order through a local cutover and unsafe fallback."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from lab import cents, return_to_source_if_reconciled, select_if_reconciled, transform
from reverse_lab import replay_target_to_source


def handler_for(folder: Path, pointer: Path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def send_json(self, status: int, payload: dict):
            body = json.dumps(payload, sort_keys=True).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def selected(self):
            name = pointer.read_text()
            if name not in {'source.sqlite', 'target.sqlite'}:
                raise ValueError('Unknown local selection')
            return name, folder / name

        def do_GET(self):
            if not self.path.startswith('/orders/') or '/' in self.path[len('/orders/'):]:
                self.send_json(404, {'error': 'unknown_route'})
                return
            order_id = self.path[len('/orders/'):]
            name, path = self.selected()
            with sqlite3.connect(path) as db:
                field = 'amount' if name == 'source.sqlite' else 'amount_cents'
                row = db.execute(f'SELECT {field} FROM orders WHERE id=?', (order_id,)).fetchone()
            if row is None:
                self.send_json(404, {'error': 'missing_order', 'serving': name})
                return
            amount = cents(row[0]) if name == 'source.sqlite' else row[0]
            self.send_json(200, {'id': order_id, 'amount_cents': amount, 'serving': name})

        def do_POST(self):
            if self.path != '/orders':
                self.send_json(404, {'error': 'unknown_route'})
                return
            name, path = self.selected()
            if name != 'target.sqlite':
                self.send_json(409, {'error': 'write_path_not_in_fixture'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if size < 1 or size > 1024:
                    raise ValueError('Invalid request size')
                payload = json.loads(self.rfile.read(size))
                order_id = payload['id']
                if not isinstance(order_id, str) or not order_id.isalnum():
                    raise ValueError('Invalid order ID')
                amount = cents(payload['amount'])
                with sqlite3.connect(path) as db:
                    db.execute('INSERT INTO orders VALUES (?,?)', (order_id, amount))
            except (ValueError, KeyError, TypeError, sqlite3.IntegrityError):
                self.send_json(400, {'error': 'invalid_or_duplicate_order'})
                return
            self.send_json(201, {'id': order_id, 'amount_cents': amount, 'serving': name})

    return Handler


def fetch(url: str):
    try:
        with urlopen(url, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def run(folder: Path):
    source = folder / 'source.sqlite'
    target = folder / 'target.sqlite'
    pointer = folder / 'selected.txt'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount TEXT NOT NULL)')
        db.executemany('INSERT INTO orders VALUES (?,?)', [('a', '12.99'), ('b', '0.01')])
    pointer.write_text(source.name)
    transform(source, target, cents)
    # A late old-side write blocks cutover until the target catches up.
    with sqlite3.connect(source) as db:
        db.execute('INSERT INTO orders VALUES (?,?)', ('d', '3.50'))
    assert not select_if_reconciled(source, target, pointer)
    with sqlite3.connect(target) as db:
        db.execute('INSERT INTO orders VALUES (?,?)', ('d', 350))
    assert select_if_reconciled(source, target, pointer)

    server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(folder, pointer))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    try:
        selected_before = fetch(base + '/orders/d')
        assert selected_before == (200, {'id': 'd', 'amount_cents': 350,
                                         'serving': 'target.sqlite'})
        request = Request(base + '/orders',
                          data=json.dumps({'id': 'e', 'amount': '2.50'}).encode(),
                          headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(request, timeout=3) as response:
            confirmed = (response.status, json.load(response))
        assert confirmed == (201, {'id': 'e', 'amount_cents': 250,
                                   'serving': 'target.sqlite'})
        # A cautious fallback stays on target while the source is missing e.
        guarded_fallback = not return_to_source_if_reconciled(source, target, pointer)
        assert pointer.read_text() == target.name
        selected_after = fetch(base + '/orders/e')
        assert selected_after[0] == 200
        # Negative control: force the same local visitor route to the old store.
        pointer.write_text(source.name)
        unsafe_fallback = fetch(base + '/orders/e')
        assert unsafe_fallback == (404, {'error': 'missing_order', 'serving': 'source.sqlite'})
        pointer.write_text(target.name)
        restored = fetch(base + '/orders/e')
        assert restored[0] == 200
        # Once the toy target stops receiving writes, replay its missing row.
        assert replay_target_to_source(source, target) == 1
        assert return_to_source_if_reconciled(source, target, pointer)
        safe_local_return = fetch(base + '/orders/e')
        assert safe_local_return == (200, {'id': 'e', 'amount_cents': 250,
                                            'serving': 'source.sqlite'})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    return {'late_source_write_blocked_cutover': True,
            'target_customer_read': selected_before[0],
            'target_write_confirmation': confirmed[0],
            'guarded_fallback_blocked': guarded_fallback,
            'forced_old_route_after_confirmation': unsafe_fallback[0],
            'target_route_restored': restored[0],
            'replayed_order_visible_after_guarded_local_return': safe_local_return[0],
            'scope': 'sequential loopback HTTP and SQLite with trusted local selection; no writer fence, DNS, CDC, concurrent clients, cloud or external-effect recovery'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-cutover-visitor-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result, sort_keys=True))
