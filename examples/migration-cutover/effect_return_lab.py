"""Local migration return with a separate fictional payment-effect receipt."""

from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from lab import reconciles, return_to_source_if_reconciled
from reverse_lab import fixture, replay_target_to_source


class ReplyLost(RuntimeError):
    pass


OPERATION = 'authorize:e:250'


def setup(folder: Path):
    source, target, pointer = fixture(folder)
    provider = folder / 'provider.sqlite'
    for path in (source, target):
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('''CREATE TABLE effect_receipts(
                operation TEXT PRIMARY KEY, order_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL, receipt TEXT, state TEXT NOT NULL)''')
    with closing(sqlite3.connect(target)) as db, db:
        db.execute('INSERT INTO effect_receipts VALUES (?,?,?,?,?)',
                   (OPERATION, 'e', 250, None, 'unknown'))
    with closing(sqlite3.connect(provider)) as db, db:
        db.execute('''CREATE TABLE authorizations(
            operation TEXT PRIMARY KEY, order_id TEXT NOT NULL,
            amount_cents INTEGER NOT NULL, receipt TEXT NOT NULL)''')
    return source, target, pointer, provider


def provider_authorize(provider: Path, *, lose_reply=False):
    """A fictional provider commits before the optional lost response."""
    receipt = hashlib.sha256(f'{OPERATION}:e:250'.encode()).hexdigest()
    expected = ('e', 250, receipt)
    with closing(sqlite3.connect(provider)) as db, db:
        row = db.execute('SELECT order_id,amount_cents,receipt FROM authorizations WHERE operation=?',
                         (OPERATION,)).fetchone()
        if row is not None and row != expected:
            raise ValueError('provider operation conflict')
        if row is None:
            db.execute('INSERT INTO authorizations VALUES (?,?,?,?)', (OPERATION, *expected))
    if lose_reply:
        raise ReplyLost('Provider committed; application response was lost')
    return receipt


def confirm_target(target: Path, provider: Path | None):
    """An absent or unavailable provider lookup leaves the target outcome unknown."""
    if provider is None:
        return 'unknown'
    with closing(sqlite3.connect(provider)) as db:
        row = db.execute('SELECT order_id,amount_cents,receipt FROM authorizations WHERE operation=?',
                         (OPERATION,)).fetchone()
    if row is None:
        return 'unknown'
    expected = ('e', 250, hashlib.sha256(f'{OPERATION}:e:250'.encode()).hexdigest())
    if row != expected:
        return 'conflict'
    with closing(sqlite3.connect(target)) as db, db:
        local = db.execute('SELECT order_id,amount_cents,receipt,state FROM effect_receipts WHERE operation=?',
                           (OPERATION,)).fetchone()
        if local not in (('e', 250, None, 'unknown'), ('e', 250, row[2], 'confirmed')):
            return 'conflict'
        db.execute("UPDATE effect_receipts SET receipt=?,state='confirmed' WHERE operation=?",
                   (row[2], OPERATION))
    return 'confirmed'


def replay_confirmed_receipt(source: Path, target: Path):
    with closing(sqlite3.connect(target)) as db:
        row = db.execute('SELECT operation,order_id,amount_cents,receipt,state '
                         'FROM effect_receipts WHERE operation=?', (OPERATION,)).fetchone()
    if row is None or row[4] != 'confirmed' or not row[3]:
        raise ValueError('Target has no confirmed provider receipt')
    with closing(sqlite3.connect(source)) as db, db:
        old = db.execute('SELECT operation,order_id,amount_cents,receipt,state '
                         'FROM effect_receipts WHERE operation=?', (OPERATION,)).fetchone()
        if old is not None and old != row:
            raise ValueError('Old application receipt conflicts with target')
        if old is None:
            db.execute('INSERT INTO effect_receipts VALUES (?,?,?,?,?)', row)
            return 1
    return 0


def guarded_return(source: Path, target: Path, pointer: Path, provider: Path | None):
    if not reconciles(source, target) or provider is None:
        return False
    with closing(sqlite3.connect(target)) as db:
        target_rows = db.execute('SELECT * FROM effect_receipts ORDER BY operation').fetchall()
    with closing(sqlite3.connect(source)) as db:
        source_rows = db.execute('SELECT * FROM effect_receipts ORDER BY operation').fetchall()
    if not target_rows or target_rows != source_rows or any(
            row[4] != 'confirmed' or not row[3] for row in target_rows):
        return False
    with closing(sqlite3.connect(provider)) as db:
        provider_rows = db.execute('SELECT * FROM authorizations ORDER BY operation').fetchall()
    if [(r[0], r[1], r[2], r[3]) for r in target_rows] != provider_rows:
        return False
    return return_to_source_if_reconciled(source, target, pointer)


def run(folder: Path):
    source, target, pointer, provider = setup(folder)
    assert replay_target_to_source(source, target) == 2
    assert reconciles(source, target)
    assert not guarded_return(source, target, pointer, provider)
    try:
        provider_authorize(provider, lose_reply=True)
    except ReplyLost:
        pass
    else:
        raise AssertionError('Expected simulated lost response')
    assert not guarded_return(source, target, pointer, provider)
    assert confirm_target(target, provider) == 'confirmed'
    assert not guarded_return(source, target, pointer, provider)
    assert replay_confirmed_receipt(source, target) == 1
    assert replay_confirmed_receipt(source, target) == 0
    assert guarded_return(source, target, pointer, provider)
    assert pointer.read_text() == source.name
    return {'orders_match_before_effect_check': True,
            'lost_provider_reply_blocked_return': True,
            'confirmed_but_unreplayed_receipt_blocked_return': True,
            'receipt_replay_retry_added': 0,
            'guarded_local_return_after_data_and_effect_reconciliation': True,
            'scope': 'sequential SQLite fixture; no real payment, independent writer fence, DNS, AWS or customer recovery'}


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-migration-effect-') as temp:
        folder = Path(temp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    print(json.dumps(result, sort_keys=True))
