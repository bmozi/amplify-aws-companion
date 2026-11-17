"""Two-ledger stock timeout lesson. Local SQLite fixtures; no AWS or real depot."""

import json
from pathlib import Path
import sqlite3
import tempfile


class ReplyLost(Exception):
    """No authoritative stock reply arrived; the caller cannot infer an outcome."""


def database(path):
    return sqlite3.connect(path, timeout=3)


class StockSystem:
    def __init__(self, path):
        self.path = Path(path)
        with database(self.path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS stock (depot TEXT PRIMARY KEY, available INTEGER NOT NULL);
                INSERT OR IGNORE INTO stock VALUES ('depot-1', 1);
                CREATE TABLE IF NOT EXISTS decisions (
                    operation_id TEXT PRIMARY KEY, request_id TEXT NOT NULL,
                    depot TEXT NOT NULL, outcome TEXT NOT NULL
                );
            """)

    def reserve(self, operation_id, request_id, depot, *, lose_reply=False):
        if depot != 'depot-1':
            raise ValueError('Unknown depot')
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute(
                'SELECT request_id,depot,outcome FROM decisions WHERE operation_id=?',
                (operation_id,)
            ).fetchone()
            if previous:
                if previous[:2] != (request_id, depot):
                    raise ValueError('Operation ID reused for different intent')
                outcome = previous[2]
            else:
                available = db.execute(
                    'SELECT available FROM stock WHERE depot=?', (depot,)
                ).fetchone()[0]
                outcome = 'reserved' if available else 'unavailable'
                if available:
                    db.execute('UPDATE stock SET available=available-1 WHERE depot=?', (depot,))
                db.execute('INSERT INTO decisions VALUES (?,?,?,?)',
                           (operation_id, request_id, depot, outcome))
        if lose_reply:
            raise ReplyLost('Stock decision committed; reply lost')
        return outcome

    def lookup(self, operation_id):
        with database(self.path) as db:
            return db.execute(
                'SELECT request_id,depot,outcome FROM decisions WHERE operation_id=?',
                (operation_id,)
            ).fetchone()

    def available(self):
        with database(self.path) as db:
            return db.execute("SELECT available FROM stock WHERE depot='depot-1'").fetchone()[0]


class PickupCoordinator:
    def __init__(self, path):
        self.path = Path(path)
        with database(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS pickups (
                request_id TEXT PRIMARY KEY, depot TEXT NOT NULL,
                operation_id TEXT NOT NULL UNIQUE, status TEXT NOT NULL
            )""")

    def accept(self, request_id, depot):
        if depot != 'depot-1' or not request_id:
            raise ValueError('Invalid request')
        operation_id = 'reserve:' + request_id
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT depot,operation_id,status FROM pickups WHERE request_id=?',
                             (request_id,)).fetchone()
            if row:
                if row[:2] != (depot, operation_id):
                    raise ValueError('Request intent changed')
                return row[2]
            db.execute('INSERT INTO pickups VALUES (?,?,?,?)',
                       (request_id, depot, operation_id, 'pending_inventory'))
        return 'pending_inventory'

    def status(self, request_id):
        with database(self.path) as db:
            row = db.execute('SELECT status FROM pickups WHERE request_id=?',
                             (request_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown request')
        return row[0]

    def dispatch(self, request_id, stock, *, lose_reply=False):
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT depot,operation_id,status FROM pickups WHERE request_id=?',
                             (request_id,)).fetchone()
            if row is None:
                raise ValueError('Unknown request')
            depot, operation_id, status = row
            if status in ('reserved', 'unavailable'):
                return status
            # Commit uncertainty locally before calling the other ledger.
            db.execute("UPDATE pickups SET status='stock_unknown' WHERE request_id=?",
                       (request_id,))
        try:
            outcome = stock.reserve(operation_id, request_id, depot, lose_reply=lose_reply)
        except ReplyLost:
            return 'stock_unknown'
        return self._record(request_id, outcome)

    def reconcile(self, request_id, stock, *, query_available=True):
        with database(self.path) as db:
            row = db.execute('SELECT depot,operation_id,status FROM pickups WHERE request_id=?',
                             (request_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown request')
        depot, operation_id, status = row
        if status in ('reserved', 'unavailable'):
            return status
        if not query_available:
            return status  # no second reservation with a fresh ID
        try:
            decision = stock.lookup(operation_id)
        except ReplyLost:
            return status  # provider may be down; absence of a reply proves nothing
        if decision is None:
            return status  # this fixture does not infer failure from absence
        if decision[:2] != (request_id, depot):
            raise ValueError('External decision does not match request')
        return self._record(request_id, decision[2])

    def _record(self, request_id, outcome):
        if outcome not in ('reserved', 'unavailable'):
            raise ValueError('Invalid stock outcome')
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            old = db.execute('SELECT status FROM pickups WHERE request_id=?',
                             (request_id,)).fetchone()[0]
            if old in ('reserved', 'unavailable') and old != outcome:
                raise ValueError('Conflicting stock outcome')
            db.execute('UPDATE pickups SET status=? WHERE request_id=?',
                       (outcome, request_id))
        return outcome


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-external-stock-') as raw:
        folder = Path(raw)
        pickup_path, stock_path = folder / 'pickup.sqlite', folder / 'stock.sqlite'
        pickup, stock = PickupCoordinator(pickup_path), StockSystem(stock_path)
        assert pickup.accept('request-a', 'depot-1') == 'pending_inventory'
        uncertain = pickup.dispatch('request-a', stock, lose_reply=True)
        assert uncertain == 'stock_unknown' and stock.available() == 0
        assert pickup.reconcile('request-a', stock, query_available=False) == 'stock_unknown'
        pickup, stock = PickupCoordinator(pickup_path), StockSystem(stock_path)
        recovered = pickup.reconcile('request-a', stock)
        assert recovered == 'reserved' and pickup.dispatch('request-a', stock) == 'reserved'
        assert pickup.accept('request-b', 'depot-1') == 'pending_inventory'
        second = pickup.dispatch('request-b', stock)
        assert second == 'unavailable' and stock.available() == 0
        return {'after_lost_reply': uncertain, 'when_lookup_unavailable': 'stock_unknown',
                'after_reopen_and_lookup': recovered, 'second_request': second,
                'remaining_boxes': stock.available(),
                'scope': 'two same-machine SQLite ledgers; no real stock API, network failure, authentication or AWS'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
