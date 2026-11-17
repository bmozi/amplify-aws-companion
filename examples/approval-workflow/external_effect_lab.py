"""Two-reviewer admission followed by a separate, simulated publisher store.

Both databases and all identities are local fixtures. No external API is called.
"""

from contextlib import closing
from hashlib import sha256
from pathlib import Path
import sqlite3
import sys
import tempfile

from two_reviewer_lab import admit, digest, review


class ReplyLost(Exception):
    pass


def initialize(local, provider, action):
    with closing(sqlite3.connect(local)) as db, db:
        db.executescript('''
            CREATE TABLE actions(id TEXT PRIMARY KEY, requester TEXT, revision INTEGER,
                digest TEXT, state TEXT);
            CREATE TABLE eligibility(actor TEXT PRIMARY KEY, active INTEGER);
            CREATE TABLE reviews(action TEXT, revision INTEGER, actor TEXT, digest TEXT,
                expires INTEGER, PRIMARY KEY(action, revision, actor));
            CREATE TABLE admissions(action TEXT PRIMARY KEY, revision INTEGER, digest TEXT);
            CREATE TABLE dispatch(operation TEXT PRIMARY KEY, action TEXT UNIQUE,
                digest TEXT, destination TEXT, artifact TEXT, state TEXT, receipt TEXT);
            INSERT INTO eligibility VALUES ('requester',1),('A',1),('B',1);
        ''')
        db.execute('INSERT INTO actions VALUES (?,?,?,?,?)',
                   (action['id'], 'requester', action['revision'], digest(action), 'pending'))
    with closing(sqlite3.connect(provider)) as db, db:
        db.execute('''CREATE TABLE effects(operation TEXT PRIMARY KEY, digest TEXT,
            destination TEXT, artifact TEXT, receipt TEXT)''')


def prepare(local, action):
    """Persist one stable operation only for the exact admitted action."""
    action_digest = digest(action)
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('''SELECT a.revision,a.digest,a.state,m.revision,m.digest
            FROM actions a LEFT JOIN admissions m ON m.action=a.id
            WHERE a.id=?''', (action['id'],)).fetchone()
        if row != (action['revision'], action_digest, 'admitted',
                   action['revision'], action_digest):
            raise ValueError('action is not admitted at this exact revision')
        operation = f"publish:{action['id']}:{action['revision']}:{action_digest}"
        existing = db.execute('SELECT operation,digest,destination,artifact FROM dispatch WHERE action=?',
                              (action['id'],)).fetchone()
        if existing:
            if existing != (operation, action_digest, action['destination'], action['artifact']):
                raise ValueError('dispatch identity conflict')
            return operation
        db.execute('INSERT INTO dispatch VALUES (?,?,?,?,?,?,NULL)',
                   (operation, action['id'], action_digest, action['destination'],
                    action['artifact'], 'pending'))
        return operation


def publish(provider, operation, action, lose_reply=False):
    """A fixture provider commits before the optional simulated reply loss."""
    action_digest = digest(action)
    receipt = sha256(f'{operation}:{action_digest}'.encode()).hexdigest()
    with closing(sqlite3.connect(provider, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT digest,destination,artifact,receipt FROM effects WHERE operation=?',
                         (operation,)).fetchone()
        expected = (action_digest, action['destination'], action['artifact'], receipt)
        if old and old != expected:
            raise ValueError('provider idempotency-key conflict')
        if not old:
            db.execute('INSERT INTO effects VALUES (?,?,?,?,?)', (operation, *expected))
    if lose_reply:
        raise ReplyLost('provider committed but caller did not receive the reply')
    return receipt


def mark_unknown(local, operation):
    with closing(sqlite3.connect(local)) as db, db:
        db.execute("UPDATE dispatch SET state='unknown' WHERE operation=? AND state!='confirmed'",
                   (operation,))


def reconcile(local, provider, operation):
    """Confirm only a matching provider record; absence is still uncertain."""
    with closing(sqlite3.connect(local, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        local_row = db.execute('SELECT digest,destination,artifact,state FROM dispatch WHERE operation=?',
                               (operation,)).fetchone()
        if local_row is None:
            raise ValueError('unknown local operation')
        if provider is None:
            return 'unknown'
        with closing(sqlite3.connect(provider)) as remote:
            effect = remote.execute('SELECT digest,destination,artifact,receipt FROM effects WHERE operation=?',
                                    (operation,)).fetchone()
        if effect is None:
            return 'unknown'  # A missed/late provider read does not prove no effect.
        expected_receipt = sha256(f'{operation}:{local_row[0]}'.encode()).hexdigest()
        if effect != (*local_row[:3], expected_receipt):
            return 'conflict'
        db.execute("UPDATE dispatch SET state='confirmed',receipt=? WHERE operation=?",
                   (effect[3], operation))
        return 'confirmed'


def state(local, operation):
    with closing(sqlite3.connect(local)) as db:
        return db.execute('SELECT state FROM dispatch WHERE operation=?',
                          (operation,)).fetchone()[0]


def effect_count(provider):
    with closing(sqlite3.connect(provider)) as db:
        return db.execute('SELECT count(*) FROM effects').fetchone()[0]


def example_action():
    return {'id': 'price-list-7', 'revision': 1, 'artifact': 'fixture-sha256-v1',
            'destination': 'training-site', 'effective_date': 'fictional-day-2'}


def run(local, provider):
    action = example_action()
    initialize(local, provider, action)
    try:
        prepare(local, action)
    except ValueError:
        print('No admission: dispatch refused.')
    else:
        raise AssertionError('dispatched without approval')
    for actor in ('A', 'B'):
        assert review(local, action['id'], actor, digest(action), 10, 100) == 'reviewed'
    assert admit(local, action['id'], 20) == 'admitted'
    operation = prepare(local, action)
    try:
        publish(provider, operation, action, lose_reply=True)
    except ReplyLost:
        mark_unknown(local, operation)
    assert state(local, operation) == 'unknown' and effect_count(provider) == 1
    print('Publisher committed; reply lost; local outcome remains unknown.')
    assert reconcile(local, provider, operation) == 'confirmed'
    assert publish(provider, operation, action)  # Same key returns the same receipt.
    assert prepare(local, action) == operation and effect_count(provider) == 1
    print('Matching provider lookup confirms one effect; replay adds none.')


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without Python optimization; this drill uses assertions.')
    with tempfile.TemporaryDirectory(prefix='approval-effect-') as temporary:
        run(Path(temporary) / 'admission.db', Path(temporary) / 'publisher.db')
    print('PASS: local fixture removed; no external publication or AWS call.')
