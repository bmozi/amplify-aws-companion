"""Real local FTS5 queries with stale-index and tenant negative controls; no AWS."""
import sqlite3
import sys
from fractions import Fraction
from contextlib import closing


def retrieval_metrics(returned, relevant, corpus):
    """Whole-result-set metrics for an explicitly judged, closed fixture corpus."""
    returned, relevant, corpus = set(returned), set(relevant), set(corpus)
    if not returned <= corpus or not relevant <= corpus:
        raise ValueError('Result and judgment IDs must belong to the fixture corpus')
    found = returned & relevant
    return (Fraction(len(found), len(returned)) if returned else None,
            Fraction(len(found), len(relevant)) if relevant else None)


def evaluate_retrieval():
    # Authored judgments for this intent, not customer ratings or universal truth.
    corpus = {
        11: 'Refund instructions: get your money back after returning an item.',
        12: 'Returns procedure: send the item with its receipt to receive your money.',
        13: 'Investment returns: the annual financial performance report.',
        14: 'Delivery schedule: parcels arrive on weekdays.',
    }
    relevant = {11, 12}  # intent: how can I get my money back for an item?
    with closing(sqlite3.connect(':memory:')) as db:
        db.execute('CREATE VIRTUAL TABLE evaluation USING fts5(body)')
        db.executemany('INSERT INTO evaluation(rowid, body) VALUES (?, ?)', corpus.items())
        # Fixed experiment-owned expressions; the public phrase API stays unchanged.
        cases = [('exact', '"refund"', {11}, (Fraction(1), Fraction(1, 2))),
                 ('expanded', '"refund" OR "returns"', {11, 12, 13}, (Fraction(2, 3), Fraction(1))),
                 ('unmatched', '"reimbursement"', set(), (None, Fraction(0)))]
        for name, query, expected_ids, expected_metrics in cases:
            rows = db.execute('SELECT rowid FROM evaluation WHERE evaluation MATCH ? ORDER BY rowid',
                              (query,)).fetchall()
            returned = {row[0] for row in rows}
            assert returned == expected_ids, (name, returned)
            measured = retrieval_metrics(returned, relevant, corpus)
            assert measured == expected_metrics, (name, measured)
            print('Judged retrieval:', name, 'IDs=', sorted(returned),
                  'precision=', measured[0], 'recall=', measured[1])
        # A high recall alone cannot distinguish useful retrieval from returning everything.
        assert retrieval_metrics(corpus, relevant, corpus) == (Fraction(1, 2), Fraction(1))
        assert retrieval_metrics(set(), set(), corpus) == (None, None)
        try:
            retrieval_metrics({999}, relevant, corpus)
        except ValueError:
            pass
        else:
            raise AssertionError('An unknown result ID was accepted')
    print('PASS: authored four-document judgments; no ranking, user study or cloud quality claim')


def phrase(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 100:
        raise ValueError('Supply a nonempty phrase of at most 100 characters')
    # Bind SQL values AND quote the independent FTS query language.
    return '"' + text.replace('"', '""') + '"'


def search(db, tenant, text):
    return db.execute('''
        SELECT d.id, d.body FROM search_index
        JOIN documents d ON d.id = search_index.rowid
        WHERE search_index MATCH ? AND d.tenant = ?
          AND d.revision = search_index.revision
        ORDER BY d.id
    ''', (phrase(text), tenant)).fetchall()


def synchronize(db, doc_id, fail=False):
    # Only index operations are atomic here; source changes can precede this worker.
    with db:
        db.execute('DELETE FROM search_index WHERE rowid = ?', (doc_id,))
        if fail:
            raise RuntimeError('Simulated index worker failure after removal')
        row = db.execute('SELECT id, revision, body FROM documents WHERE id = ?',
                         (doc_id,)).fetchone()
        if row:
            db.execute('INSERT INTO search_index(rowid, revision, body) VALUES (?, ?, ?)', row)


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O; this lab uses assertions')
    db = sqlite3.connect(':memory:')
    try:
        db.execute('CREATE TABLE documents(id INTEGER PRIMARY KEY, tenant TEXT, revision INTEGER, body TEXT)')
        try:
            db.execute('CREATE VIRTUAL TABLE search_index USING fts5(revision UNINDEXED, body)')
        except sqlite3.OperationalError as error:
            raise RuntimeError('This exercise requires Python SQLite compiled with FTS5; no extension is downloaded') from error
        fixtures = [(1, 'shop-a', 1, 'Returns accepted for thirty days'),
                    (2, 'shop-b', 1, 'Returns accepted for ninety days'),
                    (3, 'shop-a', 1, 'Delivery takes five days')]
        db.executemany('INSERT INTO documents VALUES (?, ?, ?, ?)', fixtures)
        db.commit()
        for doc_id, *_ in fixtures:
            synchronize(db, doc_id)
        assert search(db, 'shop-a', 'returns') == [(1, fixtures[0][3])]
        assert search(db, 'shop-b', 'returns') == [(2, fixtures[1][3])]
        assert search(db, 'unknown-shop', 'returns') == []
        unsafe = db.execute('SELECT rowid FROM search_index WHERE search_index MATCH ?',
                            (phrase('returns'),)).fetchall()
        assert unsafe == [(1,), (2,)]
        print('Tenant negative control: raw index exposes IDs 1 and 2; scoped query returns only ID 1')

        # This input is a literal phrase, not a Boolean expression chosen by a caller.
        assert search(db, 'shop-a', 'returns OR delivery') == []
        assert search(db, 'shop-a', 'returns" OR "delivery') == []
        assert search(db, "shop-a' OR 1=1 --", 'returns') == []
        print('Query boundaries: literal phrases and SQL-bound tenant values preserve fixture expectations')

        with db:
            db.execute('UPDATE documents SET revision=2, body=? WHERE id=1',
                       ('Exchanges accepted for fourteen days',))
        assert db.execute('SELECT rowid FROM search_index WHERE search_index MATCH ?',
                          (phrase('returns'),)).fetchall() == [(1,), (2,)]
        assert search(db, 'shop-a', 'returns') == []
        assert search(db, 'shop-a', 'exchanges') == []
        print('Lag: old term suppressed; new term absent until synchronization (temporary missed result)')

        before = db.execute('SELECT rowid, revision, body FROM search_index ORDER BY rowid').fetchall()
        try:
            synchronize(db, 1, fail=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Failure injection did not execute')
        assert db.execute('SELECT rowid, revision, body FROM search_index ORDER BY rowid').fetchall() == before
        synchronize(db, 1)
        synchronize(db, 1)  # replay replaces the same document identity
        assert search(db, 'shop-a', 'exchanges') == [(1, 'Exchanges accepted for fourteen days')]
        assert search(db, 'shop-a', 'returns') == []
        assert db.execute('SELECT count(*) FROM search_index WHERE rowid=1').fetchone() == (1,)
        print('Recovery: failed replacement rolls back; repeated synchronization creates one current entry')

        with db:
            db.execute('DELETE FROM documents WHERE id=1')
        assert db.execute('SELECT rowid FROM search_index WHERE search_index MATCH ?',
                          (phrase('exchanges'),)).fetchall() == [(1,)]
        assert search(db, 'shop-a', 'exchanges') == []
        synchronize(db, 1)
        assert db.execute('SELECT rowid FROM search_index WHERE rowid=1').fetchall() == []
        assert search(db, 'shop-b', 'returns') == [(2, fixtures[1][3])]
        assert search(db, 'shop-a', 'delivery') == [(3, fixtures[2][3])]
        print('Deletion: authoritative join hides deleted document before index cleanup; other documents preserved')
        print('PASS: real SQLite', sqlite3.sqlite_version, 'FTS5; sequential fixtures, no authentication or AWS evidence')
    finally:
        db.close()


if __name__ == '__main__':
    run()
    evaluate_retrieval()
