"""Sequential local replay of target edits and tombstones into an old store.

This fixture supplies its own change journal. It does not capture real CDC or
fence independent writers, so a passing pointer guard is not a cloud rollback.
"""

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile


class ChangeConflict(ValueError):
    pass


class ReplayInterrupted(RuntimeError):
    pass


SCHEMA = """CREATE TABLE orders (
    id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL,
    revision INTEGER NOT NULL, deleted INTEGER NOT NULL CHECK (deleted IN (0,1)));
CREATE TABLE changes (
    sequence INTEGER PRIMARY KEY, order_id TEXT NOT NULL,
    previous_revision INTEGER NOT NULL, previous_amount INTEGER,
    action TEXT NOT NULL CHECK (action IN ('create','update','delete')),
    amount_cents INTEGER);"""

# An event states both the previous value and the new action. Sequence order is
# supplied by this fixture, not discovered from an external source system.
EVENTS = (
    (1, 'e', 1, 250, 'update', 300),
    (2, 'f', 1, 375, 'delete', None),
    (3, 'g', 0, None, 'create', 425),
)


def rows(db):
    return db.execute('SELECT id,amount_cents,revision,deleted FROM orders ORDER BY id').fetchall()


def journal(db):
    return db.execute('SELECT sequence,order_id,previous_revision,previous_amount,'
                      'action,amount_cents FROM changes ORDER BY sequence').fetchall()


def apply(db, event):
    sequence, order_id, before_revision, before_amount, action, after_amount = event
    prior = db.execute('SELECT amount_cents,revision,deleted FROM orders WHERE id=?',
                       (order_id,)).fetchone()
    if action == 'create':
        if before_revision != 0 or before_amount is not None or prior is not None:
            raise ChangeConflict(f'{order_id}: create cannot reuse an existing ID or tombstone')
        if after_amount is None or after_amount < 0:
            raise ChangeConflict(f'{order_id}: invalid created amount')
        db.execute('INSERT INTO orders VALUES (?,?,1,0)', (order_id, after_amount))
    else:
        if prior != (before_amount, before_revision, 0):
            raise ChangeConflict(f'{order_id}: old value, revision or live state differs')
        if action == 'update':
            if after_amount is None or after_amount < 0:
                raise ChangeConflict(f'{order_id}: invalid updated amount')
            db.execute('UPDATE orders SET amount_cents=?,revision=? WHERE id=?',
                       (after_amount, before_revision + 1, order_id))
        elif action == 'delete':
            if after_amount is not None:
                raise ChangeConflict(f'{order_id}: delete must not set an amount')
            # Preserve the last amount and ID so a retry or unsafe recreation is visible.
            db.execute('UPDATE orders SET revision=?,deleted=1 WHERE id=?',
                       (before_revision + 1, order_id))
        else:
            raise ChangeConflict(f'{order_id}: unsupported action')
    db.execute('INSERT INTO changes VALUES (?,?,?,?,?,?)', event)


def setup(folder: Path):
    source, target, pointer = (folder / name for name in
                               ('source.sqlite', 'target.sqlite', 'selected.txt'))
    for path in (source, target):
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript(SCHEMA)
            db.executemany('INSERT INTO orders VALUES (?,?,1,0)', [('e', 250), ('f', 375)])
    with closing(sqlite3.connect(target)) as db, db:
        for event in EVENTS:
            apply(db, event)
    pointer.write_text(target.name)
    return source, target, pointer


def replay(source: Path, target: Path, *, fail_after=None):
    with closing(sqlite3.connect(target)) as db:
        expected = journal(db)
    with closing(sqlite3.connect(source)) as db:
        try:
            db.execute('BEGIN IMMEDIATE')
            existing = journal(db)
            if existing != expected[:len(existing)]:
                raise ChangeConflict('Old journal is not a prefix of the target journal')
            copied = 0
            for event in expected[len(existing):]:
                apply(db, event)
                copied += 1
                if copied == fail_after:
                    raise ReplayInterrupted('Simulated crash before old-store commit')
            db.commit()
            return copied
        except Exception:
            db.rollback()
            raise


def guarded_return(source: Path, target: Path, pointer: Path):
    with closing(sqlite3.connect(source)) as old, closing(sqlite3.connect(target)) as new:
        if rows(old) != rows(new) or journal(old) != journal(new):
            return False
        if not journal(new):
            return False
    temporary = pointer.with_suffix('.tmp')
    temporary.write_text(source.name)
    temporary.replace(pointer)
    return True


def run(folder: Path):
    source, target, pointer = setup(folder)
    assert not guarded_return(source, target, pointer)
    try:
        replay(source, target, fail_after=1)
    except ReplayInterrupted:
        pass
    else:
        raise AssertionError('Expected injected interruption')
    assert not guarded_return(source, target, pointer)
    copied = replay(source, target)
    assert copied == 3 and replay(source, target) == 0
    assert guarded_return(source, target, pointer)
    with closing(sqlite3.connect(source)) as db:
        result = rows(db)
    return {'interrupted_transaction_replayed_nothing': True,
            'changes_replayed': copied, 'retry_replayed': 0,
            'source_rows_including_tombstone': result,
            'guarded_local_return': pointer.read_text() == source.name,
            'scope': 'sequential fixture journal and SQLite stores; no CDC, writer fence, outside effect, DNS or AWS'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-versioned-return-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, sort_keys=True))
