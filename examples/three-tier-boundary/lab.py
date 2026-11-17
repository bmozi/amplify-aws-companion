"""Loopback two-worker / one-store teaching fixture; not an AWS or ALB emulator."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid


ACTORS = {'Bearer fixture-alice': 'alice', 'Bearer fixture-bob': 'bob'}


class CapacityBusy(Exception):
    pass


class StoreUnavailable(Exception):
    pass


class NoHealthyWorker(Exception):
    pass


class SharedStore:
    def __init__(self, path: Path):
        self.path = path
        # One slot is a deliberate local bottleneck, not an RDS connection limit.
        self.slot = threading.BoundedSemaphore(1)
        self.available = threading.Event()
        self.available.set()
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE repairs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, issue TEXT NOT NULL)')

    @contextmanager
    def connection(self):
        if not self.available.is_set():
            raise StoreUnavailable()
        if not self.slot.acquire(blocking=False):
            raise CapacityBusy()
        db = None
        try:
            if not self.available.is_set():
                raise StoreUnavailable()
            db = sqlite3.connect(self.path)
            yield db
            if db.in_transaction:
                db.rollback()
        finally:
            if db is not None:
                db.close()
            self.slot.release()

    @contextmanager
    def hold_slot(self):
        """Controlled test-only hold, independent of a real SQL query."""
        self.slot.acquire()
        try:
            yield
        finally:
            self.slot.release()

    def create(self, owner, issue):
        request_id = uuid.uuid4().hex
        with self.connection() as db:
            db.execute('INSERT INTO repairs VALUES (?, ?, ?)', (request_id, owner, issue))
            db.commit()
        return request_id

    def read_owned(self, owner, request_id):
        with self.connection() as db:
            return db.execute('SELECT issue FROM repairs WHERE id=? AND owner=?',
                              (request_id, owner)).fetchone()

    def probe(self):
        with self.connection() as db:
            return db.execute('SELECT 1').fetchone() == (1,)


class Worker:
    def __init__(self, name, store):
        self.name = name
        self.store = store
        self.local_receipts = {}  # Deliberately unsafe design: disappears on replacement.

    def create(self, owner, issue):
        request_id = self.store.create(owner, issue)
        self.local_receipts[request_id] = owner
        return request_id

    def local_read(self, owner, request_id):
        return request_id in self.local_receipts and self.local_receipts[request_id] == owner

    def shared_read(self, owner, request_id):
        return self.store.read_owned(owner, request_id)


class ToyRouter:
    def __init__(self, store):
        self.workers = [Worker('worker-a', store), Worker('worker-b', store)]
        self.healthy = [True, True]
        self.next_index = 0
        self.lock = threading.Lock()

    def has_healthy_worker(self):
        with self.lock:
            return any(self.healthy)

    def choose(self):
        with self.lock:
            for _ in self.workers:
                index = self.next_index
                self.next_index = (self.next_index + 1) % len(self.workers)
                if self.healthy[index]:
                    return self.workers[index]
        raise NoHealthyWorker()


def handler_for(router):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, code, value):
            data = json.dumps(value).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def actor(self):
            actor = ACTORS.get(self.headers.get('Authorization'))
            if actor is None:
                self.reply(401, {'error': 'fixture_actor_required'})
            return actor

        def do_POST(self):
            actor = self.actor()
            if actor is None:
                return
            if self.path != '/repairs':
                return self.reply(404, {'error': 'not_found'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1024:
                    raise ValueError()
                payload = json.loads(self.rfile.read(length))
                if (not isinstance(payload, dict) or set(payload) != {'issue'}
                        or not isinstance(payload['issue'], str)
                        or not 0 < len(payload['issue'].strip()) <= 120):
                    raise ValueError()
            except (ValueError, UnicodeError):
                return self.reply(400, {'error': 'invalid_request'})
            try:
                worker = router.choose()
                request_id = worker.create(actor, payload['issue'])
            except NoHealthyWorker:
                return self.reply(503, {'error': 'no_toy_worker'})
            except CapacityBusy:
                return self.reply(503, {'error': 'store_busy'})
            except StoreUnavailable:
                return self.reply(503, {'error': 'store_unavailable'})
            self.reply(201, {'request_id': request_id, 'worker': worker.name})

        def do_GET(self):
            if self.path == '/health/live':
                return self.reply(200, {'process': 'alive'})
            if self.path == '/health/ready':
                try:
                    if not router.has_healthy_worker():
                        raise NoHealthyWorker()
                    if not router.workers[0].store.probe():
                        raise StoreUnavailable()
                except NoHealthyWorker:
                    return self.reply(503, {'error': 'no_toy_worker'})
                except CapacityBusy:
                    return self.reply(503, {'error': 'store_busy'})
                except StoreUnavailable:
                    return self.reply(503, {'error': 'store_unavailable'})
                return self.reply(200, {'ready': True})
            actor = self.actor()
            if actor is None:
                return
            prefix = '/repairs/' if self.path.startswith('/repairs/') else '/local/'
            if not self.path.startswith(prefix) or not self.path[len(prefix):]:
                return self.reply(404, {'error': 'not_found'})
            request_id = self.path[len(prefix):]
            try:
                worker = router.choose()
                if prefix == '/local/':
                    found = worker.local_read(actor, request_id)
                    issue = 'worker-local-only' if found else None
                else:
                    row = worker.shared_read(actor, request_id)
                    issue = row[0] if row else None
            except NoHealthyWorker:
                return self.reply(503, {'error': 'no_toy_worker'})
            except CapacityBusy:
                return self.reply(503, {'error': 'store_busy'})
            except StoreUnavailable:
                return self.reply(503, {'error': 'store_unavailable'})
            if issue is None:
                return self.reply(404, {'error': 'not_found', 'worker': worker.name})
            self.reply(200, {'issue': issue, 'worker': worker.name})

    return Handler


@contextmanager
def running_fixture():
    with tempfile.TemporaryDirectory(prefix='three-tier-boundary-') as folder:
        store = SharedStore(Path(folder) / 'repairs.sqlite3')
        router = ToyRouter(store)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(router))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield 'http://127.0.0.1:' + str(server.server_port), store, router
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


def request(base, method, path, actor='fixture-alice', payload=None):
    body = None if payload is None else json.dumps(payload).encode('utf-8')
    req = Request(base + path, data=body, method=method,
                  headers={'Authorization': 'Bearer ' + actor, 'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        with error:
            return error.code, json.load(error)


def main():
    with running_fixture() as (base, store, router):
        code, created = request(base, 'POST', '/repairs', payload={'issue': 'pump'})
        assert code == 201 and created['worker'] == 'worker-a'
        request_id = created['request_id']
        local_code, local = request(base, 'GET', '/local/' + request_id)
        assert local_code == 404 and local['worker'] == 'worker-b'
        shared = [request(base, 'GET', '/repairs/' + request_id) for _ in range(2)]
        assert all(status == 200 for status, _ in shared)
        assert {body['worker'] for _, body in shared} == {'worker-a', 'worker-b'}
        denied, _ = request(base, 'GET', '/repairs/' + request_id, actor='fixture-bob')
        assert denied == 404
        with store.hold_slot():
            busy, _ = request(base, 'POST', '/repairs', payload={'issue': 'drain'})
            assert busy == 503
        router.healthy[0] = False
        recovered, outcome = request(base, 'GET', '/repairs/' + request_id)
        assert recovered == 200 and outcome['worker'] == 'worker-b'
        store.available.clear()
        live, _ = request(base, 'GET', '/health/live')
        ready, _ = request(base, 'GET', '/health/ready')
        unavailable, _ = request(base, 'GET', '/repairs/' + request_id)
        assert (live, ready, unavailable) == (200, 503, 503)
        store.available.set()
        restored, _ = request(base, 'GET', '/repairs/' + request_id)
        assert restored == 200
        print(json.dumps({'local_state_other_worker': local_code,
                          'shared_read_workers': sorted(body['worker'] for _, body in shared),
                          'other_actor': denied, 'busy_store': busy,
                          'unhealthy_worker_skipped': outcome['worker'],
                          'store_outage_live_ready_customer': [live, ready, unavailable],
                          'customer_read_after_store_return': restored,
                          'scope': 'loopback HTTP + SQLite fixture; no AWS behavior tested'}, indent=2))


if __name__ == '__main__':
    main()
