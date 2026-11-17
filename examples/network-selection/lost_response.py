"""Local commit-before-response process exit; separate authority counterexample.

SQLite and trusted fixture input only. No HTTP, replication, IAM or AWS.
"""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import uuid

CRASH = 73
REQUEST = {'customer': 'maya', 'slot': '10:00'}


def prepare(path):
    with closing(sqlite3.connect(path)) as db:
        db.execute('CREATE TABLE bookings (request_id TEXT PRIMARY KEY, body TEXT NOT NULL, appointment TEXT UNIQUE NOT NULL)')
        db.commit()


def book(path, request_id, body):
    encoded = json.dumps(body, sort_keys=True, separators=(',', ':'))
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        prior = db.execute('SELECT body, appointment FROM bookings WHERE request_id=?', (request_id,)).fetchone()
        if prior:
            if prior[0] != encoded:
                raise ValueError('request identity reused with different content')
            return prior[1]
        appointment = str(uuid.uuid4())
        # Receipt and business record are one row/transaction in this fixture.
        db.execute('INSERT INTO bookings VALUES (?,?,?)', (request_id, encoded, appointment))
    return appointment


def rows(path):
    with closing(sqlite3.connect(path)) as db:
        return db.execute('SELECT request_id, body, appointment FROM bookings ORDER BY request_id').fetchall()


def invoke(path, body, crash=False):
    return subprocess.run([sys.executable, str(Path(__file__).resolve()), 'worker', str(path),
                           json.dumps(body), 'crash' if crash else 'reply'],
                          text=True, capture_output=True, timeout=10)


def main():
    with tempfile.TemporaryDirectory(prefix='booking-response-') as directory:
        root = Path(directory)
        authority, stale = root/'authority.db', root/'independent.db'
        prepare(authority)
        prepare(stale)  # An empty independent store, not an implemented replica.
        lost = invoke(authority, REQUEST, crash=True)
        assert lost.returncode == CRASH and lost.stdout == ''
        committed = rows(authority)
        assert len(committed) == 1 and committed[0][0] == 'booking-42'
        assert json.loads(committed[0][1]) == REQUEST
        print('No worker response; independent inspection finds one committed booking.')

        for _ in range(2):
            retry = invoke(authority, REQUEST)
            assert retry.returncode == 0, retry.stderr
            assert json.loads(retry.stdout)['appointment'] == committed[0][2]
            assert rows(authority) == committed
        changed = invoke(authority, {**REQUEST, 'slot': '11:00'})
        assert changed.returncode != 0 and 'different content' in changed.stderr
        assert rows(authority) == committed
        print('New-process retries return the original appointment; changed content rejects.')

        assert rows(stale) == []
        unsafe = invoke(stale, REQUEST)
        assert unsafe.returncode == 0, unsafe.stderr
        second = rows(stale)
        assert len(second) == 1 and second[0][:2] == committed[0][:2]
        assert second[0][2] != committed[0][2]
        assert len(rows(authority)) + len(second) == 2
        print('Counterexample: same request ID at two independent stores creates two appointments.')
        print('Both stores remain inspectable until fixture cleanup; no merge or repair is claimed.')
    assert not root.exists()
    print('PASS: local process-exit/retry boundaries and temporary cleanup; no AWS evidence.')


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization')
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        result = book(Path(sys.argv[2]), 'booking-42', json.loads(sys.argv[3]))
        if sys.argv[4] == 'crash':
            os._exit(CRASH)  # Committed transaction; no response printed.
        print(json.dumps({'appointment': result}), flush=True)
    else:
        main()
