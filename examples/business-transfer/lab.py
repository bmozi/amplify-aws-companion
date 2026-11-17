"""Local rental invariants with fictional time and trusted staff fixtures; no AWS."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier
import sqlite3
import tempfile
import uuid

# Trusted fixtures, NOT authentication. Times are minutes on one fictional UTC day.
STAFF = {'staff-a': 'A', 'staff-b': 'B'}


def reserve(db, owner, key, asset, start, returned):
    if not owner or not key or type(start) is not int or type(returned) is not int or not 0 <= start < returned <= 1440:
        raise ValueError('Invalid bounded fixture request')
    with db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT 1 FROM assets WHERE id=?', (asset,)).fetchone():
            raise ValueError('Unknown asset')
        existing = db.execute('SELECT id,asset,start,returned FROM bookings WHERE owner=? AND retry_key=?',
                              (owner, key)).fetchone()
        if existing:
            if existing[1:] != (asset, start, returned):
                raise ValueError('Retry intent changed')
            return existing[0]
        # The check and insert share one write transaction across all assets in this model.
        conflict = db.execute('SELECT 1 FROM bookings WHERE asset=? AND start<? AND occupied_until>?',
                              (asset, returned+60, start)).fetchone()
        if conflict:
            return None
        identifier = uuid.uuid4().hex
        db.execute('INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?)',
                   (identifier, owner, key, asset, start, returned, returned+60, 'confirmed'))
        return identifier


def handover(db, staff, booking, now):
    with db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT b.asset,b.start,b.returned,b.state,a.branch,a.condition '
                         'FROM bookings b JOIN assets a ON b.asset=a.id WHERE b.id=?', (booking,)).fetchone()
        if not row or STAFF.get(staff) != row[4]:
            return 'denied'
        asset, start, returned, state, _, condition = row
        if state != 'confirmed' or not start <= now < returned:
            return 'not_eligible'
        if condition != 'ready':
            return 'exception_required'
        db.execute("UPDATE assets SET condition='out' WHERE id=?", (asset,))
        db.execute("UPDATE bookings SET state='handed_over' WHERE id=?", (booking,))
        return 'handed_over'


def record_condition(db, staff, asset, expected, replacement):
    # A bounded fixture path only; no repair approval or cross-branch transport implementation.
    if (expected, replacement) not in {('out','returned_uninspected'),
                                      ('returned_uninspected','ready'),
                                      ('returned_uninspected','blocked')}:
        raise ValueError('Unsupported transition')
    with db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT branch,condition FROM assets WHERE id=?', (asset,)).fetchone()
        if not row or STAFF.get(staff) != row[0] or row[1] != expected:
            return False
        db.execute('UPDATE assets SET condition=? WHERE id=?', (replacement, asset))
        return True


def snapshot(db):
    return (db.execute('SELECT * FROM assets ORDER BY id').fetchall(),
            db.execute('SELECT * FROM bookings ORDER BY id').fetchall())


def run():
    with tempfile.TemporaryDirectory(prefix='amplify-rental-') as directory:
        path = Path(directory)/'rental.sqlite'
        with closing(sqlite3.connect(path)) as db:
            db.executescript('''CREATE TABLE assets(id TEXT PRIMARY KEY, branch TEXT, condition TEXT);
            CREATE TABLE bookings(id TEXT PRIMARY KEY,owner TEXT,retry_key TEXT,asset TEXT,
              start INTEGER,returned INTEGER,occupied_until INTEGER,state TEXT,UNIQUE(owner,retry_key));
            INSERT INTO assets VALUES ('cleaner-1','A','ready'),('cleaner-2','B','ready');''')
            first = reserve(db, 'alice', 'first', 'cleaner-1', 540, 660)  # 09:00–11:00; occupied to noon
            assert first and reserve(db, 'alice', 'first', 'cleaner-1', 540, 660) == first
            before = snapshot(db)
            try:
                reserve(db, 'alice', 'first', 'cleaner-1', 540, 661)
            except ValueError:
                pass
            else:
                raise AssertionError('Changed retry input must conflict')
            assert snapshot(db) == before
            assert reserve(db, 'bob', 'too-early', 'cleaner-1', 719, 780) is None
            second = reserve(db, 'bob', 'boundary', 'cleaner-1', 720, 780)
            assert second
            print('09:00 rental occupies through noon: 11:59 conflicts; 12:00 touches without overlap')

            barrier = Barrier(2)
            def competing(owner):
                with closing(sqlite3.connect(path, timeout=5)) as connection:
                    barrier.wait(timeout=5)
                    return reserve(connection, owner, 'race', 'cleaner-2', 600, 660)
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(competing, ['carol', 'dave']))
            assert sum(value is not None for value in outcomes) == 1
            assert db.execute("SELECT COUNT(*) FROM bookings WHERE asset='cleaner-2'").fetchone()[0] == 1
            print('Concurrent overlapping requests: exactly one confirmation in this SQLite run')

            before = snapshot(db)
            assert handover(db, 'staff-b', first, 540) == 'denied'
            assert snapshot(db) == before
            assert handover(db, 'staff-a', first, 540) == 'handed_over'
            assert handover(db, 'staff-a', first, 541) == 'not_eligible'
            before = snapshot(db)
            assert handover(db, 'staff-a', second, 720) == 'exception_required'
            assert snapshot(db) == before, 'A late asset must not erase a later booking'
            print('Noon arrived, but the machine is still out: later booking remains confirmed; handover blocked')

            assert record_condition(db, 'staff-a', 'cleaner-1', 'out', 'returned_uninspected')
            assert handover(db, 'staff-a', second, 725) == 'exception_required'
            assert record_condition(db, 'staff-a', 'cleaner-1', 'returned_uninspected', 'blocked')
            before = snapshot(db)
            assert handover(db, 'staff-a', second, 730) == 'exception_required'
            assert not record_condition(db, 'staff-a', 'cleaner-1', 'returned_uninspected', 'ready')
            assert snapshot(db) == before
            print('Returned is not inspected; failed inspection blocks handover and stale expected-state update')

            winner = next(value for value in outcomes if value is not None)
            assert handover(db, 'staff-b', winner, 600) == 'handed_over'
            assert record_condition(db, 'staff-b', 'cleaner-2', 'out', 'returned_uninspected')
            assert record_condition(db, 'staff-b', 'cleaner-2', 'returned_uninspected', 'ready')
            later = reserve(db, 'erin', 'later', 'cleaner-2', 720, 780)
            assert handover(db, 'staff-b', later, 720) == 'handed_over'
            print('Positive control: recorded return and passed inspection permit the next eligible handover')

            # Unsafe policy control evaluated without performing another handover.
            calendar_only_would_allow = db.execute('SELECT start<=? AND returned>? FROM bookings WHERE id=?',
                                                   (730,730,second)).fetchone()[0]
            assert calendar_only_would_allow == 1
            assert handover(db, 'staff-a', second, 730) == 'exception_required'
            print('Negative control: calendar-only eligibility would wrongly allow the blocked cleaner')
    assert not Path(directory).exists()
    print('PASS: temporary database removed; no AWS, real identity, transport or physical inspection')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without -O; assertions check the exercise')
    run()
