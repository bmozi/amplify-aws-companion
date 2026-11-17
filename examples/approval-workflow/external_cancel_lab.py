"""Cancellation across an admitted action and a separate fixture publisher.

Trusted actor names and two local SQLite files are teaching inputs, not auth or AWS.
"""

from contextlib import closing
from hashlib import sha256
from pathlib import Path
import sqlite3
import sys
import tempfile

from external_effect_lab import (ReplyLost, effect_count, example_action, initialize,
                                 prepare, publish)
from two_reviewer_lab import admit, digest, review


def approved_operation(local: Path, action: dict) -> str:
    for actor in ('A', 'B'):
        assert review(local, action['id'], actor, digest(action), 10, 100) == 'reviewed'
    assert admit(local, action['id'], 20) == 'admitted'
    return prepare(local, action)


def start_dispatch(local: Path, operation: str) -> str:
    """Claim before calling a separate provider; the provider is not in this transaction."""
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT state FROM dispatch WHERE operation=?',
                         (operation,)).fetchone()
        if row is None:
            raise ValueError('unknown operation')
        if row[0] == 'pending':
            db.execute("UPDATE dispatch SET state='in_flight' WHERE operation=?", (operation,))
            return 'started'
        if row[0] in ('cancelled_before_send', 'cancel_requested'):
            return 'stopped'
        return 'already_started'


def request_cancel(local: Path, operation: str, actor: str) -> str:
    """A local reviewer can stop an unstarted send or flag an uncertain one."""
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('''SELECT d.state,a.requester FROM dispatch d
            JOIN actions a ON a.id=d.action WHERE d.operation=?''', (operation,)).fetchone()
        if row is None:
            raise ValueError('unknown operation')
        eligible = db.execute('SELECT active FROM eligibility WHERE actor=?',
                              (actor,)).fetchone()
        if actor != 'A' or eligible != (1,) or actor == row[1]:
            raise PermissionError('fixture cancellation actor is not eligible')
        state = row[0]
        if state == 'pending':
            db.execute("UPDATE dispatch SET state='cancelled_before_send' WHERE operation=?",
                       (operation,))
            return 'stopped_before_send'
        if state in ('in_flight', 'unknown'):
            db.execute("UPDATE dispatch SET state='cancel_requested' WHERE operation=?",
                       (operation,))
            return 'outcome_unknown'
        if state in ('cancel_requested', 'cancelled_before_send'):
            return 'duplicate'
        if state in ('confirmed', 'completed_after_cancel'):
            return 'too_late'
        raise ValueError(f'unexpected dispatch state: {state}')


def record_lost_reply(local: Path, operation: str) -> str:
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        state = db.execute('SELECT state FROM dispatch WHERE operation=?',
                           (operation,)).fetchone()
        if state is None:
            raise ValueError('unknown operation')
        if state[0] == 'in_flight':
            db.execute("UPDATE dispatch SET state='unknown' WHERE operation=?", (operation,))
            return 'unknown'
        if state[0] == 'cancel_requested':
            return 'cancel_requested'  # Preserve the manager's intent.
        raise ValueError('no in-flight reply to lose')


def reconcile(local: Path, provider: Path | None, operation: str) -> str:
    """A matching positive receipt proves an effect; one absent read proves nothing."""
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('''SELECT digest,destination,artifact,state FROM dispatch
            WHERE operation=?''', (operation,)).fetchone()
        if row is None:
            raise ValueError('unknown operation')
        if provider is None:
            return ('stopped_before_send' if row[3] == 'cancelled_before_send'
                    else 'outcome_unknown')
        with closing(sqlite3.connect(provider, timeout=5)) as remote:
            effect = remote.execute('''SELECT digest,destination,artifact,receipt
                FROM effects WHERE operation=?''', (operation,)).fetchone()
        if effect is None:
            return ('stopped_before_send' if row[3] == 'cancelled_before_send'
                    else 'outcome_unknown')
        if row[3] == 'cancelled_before_send':
            return 'conflict_after_stop'  # An outside path bypassed the local send gate.
        expected_receipt = sha256(f'{operation}:{row[0]}'.encode()).hexdigest()
        if effect != (*row[:3], expected_receipt):
            return 'conflict'
        next_state = ('completed_after_cancel' if row[3] == 'cancel_requested'
                      else 'confirmed')
        db.execute('UPDATE dispatch SET state=?,receipt=? WHERE operation=?',
                   (next_state, effect[3], operation))
        return next_state


def state(local: Path, operation: str) -> str:
    with closing(sqlite3.connect(local)) as db:
        return db.execute('SELECT state FROM dispatch WHERE operation=?',
                          (operation,)).fetchone()[0]


def run(root: Path) -> None:
    action = example_action()
    local, provider = root / 'workflow.db', root / 'publisher.db'
    initialize(local, provider, action)
    operation = approved_operation(local, action)
    assert start_dispatch(local, operation) == 'started'
    assert request_cancel(local, operation, 'A') == 'outcome_unknown'
    try:
        publish(provider, operation, action, lose_reply=True)
    except ReplyLost:
        assert record_lost_reply(local, operation) == 'cancel_requested'
    assert state(local, operation) == 'cancel_requested' and effect_count(provider) == 1
    assert reconcile(local, None, operation) == 'outcome_unknown'
    assert reconcile(local, provider, operation) == 'completed_after_cancel'
    assert request_cancel(local, operation, 'A') == 'too_late'
    assert effect_count(provider) == 1
    print('Cancellation was requested after dispatch started; provider effect is confirmed.')
    print('A separate correction would need its own authority and receipt.')


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization; the demonstration uses assertions.')
    with tempfile.TemporaryDirectory(prefix='approval-external-cancel-') as temporary:
        run(Path(temporary))
    print('PASS: local fixtures removed; no external publication or AWS call.')
