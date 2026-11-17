"""Local fictional payments: a crash can separate a side effect from its receipt."""
import json
import sqlite3
import tempfile
from pathlib import Path


def simulate(mode: str) -> dict:
    if mode not in {'receipt_after', 'receipt_before', 'provider_key', 'changed_key', 'changed_amount'}:
        raise ValueError('unknown scenario')
    with tempfile.TemporaryDirectory(prefix='duplicate-lesson-') as folder:
        root = Path(folder)
        with sqlite3.connect(root / 'worker.db') as worker, sqlite3.connect(root / 'provider.db') as provider:
            worker.execute('CREATE TABLE receipt (operation TEXT PRIMARY KEY)')
            provider.execute('CREATE TABLE payments (id INTEGER PRIMARY KEY, operation TEXT, provider_key TEXT UNIQUE, amount_cents INTEGER NOT NULL)')

            def send(key, amount_cents=1000):
                if key is not None:
                    prior = provider.execute(
                        'SELECT operation, amount_cents FROM payments WHERE provider_key=?', (key,)
                    ).fetchone()
                    if prior:
                        return 'replayed' if prior == ('order-17', amount_cents) else 'conflict'
                provider.execute(
                    'INSERT INTO payments(operation, provider_key, amount_cents) VALUES (?, ?, ?)',
                    ('order-17', key, amount_cents),
                )
                provider.commit()
                return 'created'

            # Simulate a crash after the first durable step. These are separate
            # databases: a worker commit cannot roll back the provider's commit.
            if mode == 'receipt_before':
                worker.execute('INSERT INTO receipt VALUES (?)', ('order-17',))
                worker.commit()  # crash before send
            else:
                send(None if mode == 'receipt_after' else 'key-17')  # crash before receipt

            already_done = worker.execute('SELECT 1 FROM receipt WHERE operation=?', ('order-17',)).fetchone()
            outcome = 'skipped_receipt'
            if not already_done:
                retry_key = None if mode == 'receipt_after' else ('key-new' if mode == 'changed_key' else 'key-17')
                outcome = send(retry_key, 1200 if mode == 'changed_amount' else 1000)
                if outcome != 'conflict':
                    worker.execute('INSERT INTO receipt VALUES (?)', ('order-17',))
                    worker.commit()
            payments = provider.execute('SELECT COUNT(*) FROM payments').fetchone()[0]
            done = bool(worker.execute('SELECT 1 FROM receipt WHERE operation=?', ('order-17',)).fetchone())
    return {'scenario': mode, 'payments': payments, 'worker_receipt': done, 'retry_outcome': outcome}


def reconcile_timeout(status: str, key_protection: str = 'active') -> dict:
    """Model a documented lookup after an ambiguous response, not a provider API."""
    observations = {
        'matching': ('found', 'order-17', 1000),
        'different_amount': ('found', 'order-17', 1200),
        'absent': ('authoritatively_absent', None, None),
        'unavailable': ('unknown', None, None),
    }
    if status not in observations:
        raise ValueError('unknown lookup scenario')
    if key_protection not in {'active', 'expired', 'unknown'}:
        raise ValueError('unknown key protection')
    state, operation, amount = observations[status]
    if state == 'found' and (operation, amount) == ('order-17', 1000):
        action = 'record_confirmed_receipt'
    elif state == 'authoritatively_absent' and key_protection == 'active':
        action = 'retry_same_key'
    else:
        action = 'hold_and_investigate'
    return {'lookup': status, 'key_protection': key_protection, 'action': action, 'key': 'key-17'}


if __name__ == '__main__':
    print(json.dumps([simulate(x) for x in ('receipt_after', 'receipt_before', 'provider_key', 'changed_key', 'changed_amount')], indent=2))
    print(json.dumps([reconcile_timeout(x) for x in ('matching', 'absent', 'unavailable', 'different_amount')], indent=2))
    print(json.dumps([reconcile_timeout('absent', x) for x in ('expired', 'unknown')], indent=2))
