"""Local out-of-order search hints; the source, not a delayed hint, supplies text."""
import sqlite3
from contextlib import closing


def new_store():
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE documents (id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, '
               'revision INTEGER NOT NULL, body TEXT NOT NULL, deleted INTEGER NOT NULL)')
    try:
        db.execute('CREATE VIRTUAL TABLE entries USING fts5(revision UNINDEXED, body)')
    except sqlite3.OperationalError as error:
        db.close()
        raise RuntimeError('Python SQLite needs FTS5; no extension is downloaded') from error
    return db


def change_source(db, *, revision, tenant, body, deleted=False):
    current = db.execute('SELECT revision FROM documents WHERE id=1').fetchone()
    if current and revision <= current[0]:
        raise ValueError('A source revision must increase')
    with db:
        db.execute('INSERT INTO documents VALUES (1,?,?,?,?) '
                   'ON CONFLICT(id) DO UPDATE SET tenant=excluded.tenant, '
                   'revision=excluded.revision, body=excluded.body, deleted=excluded.deleted',
                   (tenant, revision, body, int(deleted)))


def apply_hint(db, revision):
    """Treat the event as a wake-up hint; read the current source before indexing."""
    if type(revision) is not int or revision < 1:
        raise ValueError('Invalid event revision')
    source = db.execute('SELECT revision, body, deleted FROM documents WHERE id=1').fetchone()
    if source is None or revision > source[0]:
        raise ValueError('Event is ahead of the known source')
    if revision < source[0]:
        return 'obsolete'
    with db:
        db.execute('DELETE FROM entries WHERE rowid=1')
        if not source[2]:
            db.execute('INSERT INTO entries(rowid, revision, body) VALUES (1,?,?)',
                       (source[0], source[1]))
    return 'removed' if source[2] else 'indexed'


def search(db, tenant, word):
    # This drill accepts fixed one-word queries, not arbitrary FTS syntax.
    if word not in ('returns', 'exchanges'):
        raise ValueError('Unknown teaching query')
    return db.execute('SELECT d.id, d.body FROM entries e '
                      'JOIN documents d ON d.id=e.rowid '
                      'WHERE entries MATCH ? AND d.tenant=? AND d.deleted=0 '
                      'AND d.revision=e.revision ORDER BY d.id', (word, tenant)).fetchall()


def run():
    with closing(new_store()) as db:
        change_source(db, revision=1, tenant='shop-a', body='Returns for thirty days')
        assert apply_hint(db, 1) == 'indexed'
        change_source(db, revision=2, tenant='shop-a', body='Exchanges for fourteen days')
        change_source(db, revision=3, tenant='shop-b', body='Exchanges for seven days')
        assert apply_hint(db, 3) == 'indexed'
        assert apply_hint(db, 2) == apply_hint(db, 1) == 'obsolete'
        assert search(db, 'shop-a', 'exchanges') == []
        assert search(db, 'shop-b', 'exchanges') == [(1, 'Exchanges for seven days')]
        change_source(db, revision=4, tenant='shop-b', body='', deleted=True)
        assert search(db, 'shop-b', 'exchanges') == []  # Hide before index cleanup.
        assert apply_hint(db, 3) == 'obsolete'
        assert apply_hint(db, 4) == 'removed'
        assert db.execute('SELECT count(*) FROM entries').fetchone()[0] == 0
        print('PASS: reordered updates and delayed deletion cannot revive an old policy')
        print('Scope: one SQLite process, trusted source revisions; no AWS or network calls')


if __name__ == '__main__':
    run()
