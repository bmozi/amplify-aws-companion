"""Local reverse-data rehearsal. This is not a distributed rollback protocol."""

from pathlib import Path
import sqlite3
import tempfile

from lab import cents, new_rows, old_rows, reconciles, return_to_source_if_reconciled


class ReplayInterrupted(RuntimeError):
    pass


class ReplayConflict(ValueError):
    pass


def replay_target_to_source(source: Path, target: Path, *, fail_after=None):
    """Copy missing target rows in one local source transaction; never overwrite a conflict."""
    target_rows = new_rows(target)
    with sqlite3.connect(source) as db:
        db.execute('BEGIN IMMEDIATE')
        current = {order_id: cents(amount) for order_id, amount in
                   db.execute('SELECT id,amount FROM orders')}
        for order_id, amount in target_rows:
            if order_id in current and current[order_id] != amount:
                raise ReplayConflict(f'Conflicting amount for {order_id}')
        copied = 0
        for order_id, amount in target_rows:
            if order_id in current:
                continue
            db.execute('INSERT INTO orders VALUES (?,?)',
                       (order_id, f'{amount // 100}.{amount % 100:02d}'))
            copied += 1
            if copied == fail_after:
                raise ReplayInterrupted('Simulated interruption before source commit')
    return copied


def fixture(folder):
    source, target, pointer = (folder / name for name in
                               ('source.sqlite', 'target.sqlite', 'selected.txt'))
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount TEXT NOT NULL)')
        db.execute('INSERT INTO orders VALUES (?,?)', ('a', '12.99'))
    with sqlite3.connect(target) as db:
        db.execute('CREATE TABLE orders(id TEXT PRIMARY KEY,amount_cents INTEGER NOT NULL)')
        db.executemany('INSERT INTO orders VALUES (?,?)',
                       [('a', 1299), ('e', 250), ('f', 375)])
    pointer.write_text(target.name)
    return source, target, pointer


def run(folder):
    source, target, pointer = fixture(folder)
    assert not return_to_source_if_reconciled(source, target, pointer)
    try:
        replay_target_to_source(source, target, fail_after=1)
    except ReplayInterrupted:
        pass
    else:
        raise AssertionError('Expected simulated interruption')
    assert old_rows(source) == [('a', '12.99')]
    assert pointer.read_text() == target.name
    copied = replay_target_to_source(source, target)
    assert copied == 2 and reconciles(source, target)
    assert replay_target_to_source(source, target) == 0
    assert return_to_source_if_reconciled(source, target, pointer)
    assert pointer.read_text() == source.name
    return {'interrupted_source_transaction_rolled_back': True,
            'target_rows_replayed': copied,
            'retry_after_commit_inserted': 0,
            'guarded_local_return_selected_source': True,
            'scope': 'sequential SQLite insert-only fixture; no writer fence, CDC, external effects, DNS, AWS or customer recovery'}


if __name__ == '__main__':
    import json
    with tempfile.TemporaryDirectory(prefix='amplify-reverse-replay-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, sort_keys=True))
