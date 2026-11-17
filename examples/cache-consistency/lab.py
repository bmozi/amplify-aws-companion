"""Replay cache staleness with real SQLite writes and an explicit local schedule."""
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass(frozen=True)
class Snapshot:
    seats: int
    version: int


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE stock (tenant TEXT, item TEXT, seats INTEGER CHECK(seats >= 0), version INTEGER, PRIMARY KEY(tenant,item))')
        self.db.executemany('INSERT INTO stock VALUES (?,?,?,?)', [('a','class',1,1),('b','class',9,1)])
        self.db.commit()
        self.reads = 0

    def read(self, key):
        self.reads += 1
        row = self.db.execute('SELECT seats,version FROM stock WHERE tenant=? AND item=?', key).fetchone()
        if row is None:
            raise KeyError(key)
        return Snapshot(*row)

    def reserve(self, key):
        # The authoritative write, not the displayed snapshot, decides admission.
        with self.db:
            changed = self.db.execute('UPDATE stock SET seats=seats-1,version=version+1 WHERE tenant=? AND item=? AND seats>0', key)
        return changed.rowcount == 1


class Cache:
    def __init__(self, ttl=10):
        self.ttl = ttl
        self.entries = {}

    def get(self, key, now):
        entry = self.entries.get(key)
        if entry is None:
            return None
        value, expires = entry
        if now >= expires:
            del self.entries[key]
            return None
        return value

    def put(self, key, value, now):
        self.entries[key] = (value, now + self.ttl)

    def invalidate(self, key):
        self.entries.pop(key, None)

    def display(self, store, key, now):
        found = self.get(key, now)
        if found is not None:
            return found
        found = store.read(key)
        self.put(key, found, now)
        return found


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O: assertions are the exercise checks')
    key = ('a','class')
    with TemporaryDirectory(prefix='cache-consistency-') as directory:
        database = Path(directory) / 'stock.sqlite'
        store = Store(database)
        try:
            cache = Cache()
            assert cache.display(store,key,0) == Snapshot(1,1)
            assert cache.display(store,key,1) == Snapshot(1,1)
            assert store.reads == 1
            assert cache.display(store,('b','class'),1) == Snapshot(9,1)
            assert store.reads == 2
            print('PASS: a hit avoids a source read; tenant keys remain separate')

            assert store.reserve(key)
            assert cache.display(store,key,9) == Snapshot(1,1)
            assert not store.reserve(key)
            assert store.read(key) == Snapshot(0,2)
            print('PASS: stale display cannot authorize a second reservation')
            assert cache.display(store,key,10) == Snapshot(0,2)
            print('PASS: exact TTL boundary reloads authoritative data')

            # Reset fixture; interleave a reader and writer explicitly, without threads.
            with store.db:
                store.db.execute('UPDATE stock SET seats=1,version=3 WHERE tenant=? AND item=?', key)
            cache.invalidate(key)
            pending_reader = store.read(key)  # Reader pauses before publishing its result.
            assert store.reserve(key)        # Writer commits newer data.
            cache.invalidate(key)            # Writer deletes any existing cache entry.
            cache.put(key,pending_reader,20) # Old reader resumes AFTER invalidation.
            assert cache.display(store,key,21) == Snapshot(1,3)
            assert store.read(key) == Snapshot(0,4)
            assert not store.reserve(key)
            print('PASS: deterministic invalidation race reproduces stale repopulation')
            assert cache.display(store,key,30) == Snapshot(0,4)
            print('PASS: expiry eventually refreshes this bounded schedule')

            before = dict(cache.entries)
            try:
                cache.display(store,('a','missing'),31)
            except KeyError:
                pass
            else:
                raise AssertionError('Missing source record must not become a success')
            assert cache.entries == before
            print('PASS: failed source read creates no cache entry')
        finally:
            store.db.close()
    assert not database.exists()
    print('PASS: temporary database removed; no AWS, network, benchmark or concurrent-engine claim')


if __name__ == '__main__':
    run()
