"""Synthetic batch rerun and publication gate in one local SQLite database."""

import hashlib
import json
import sqlite3


def open_store():
    db = sqlite3.connect(':memory:')
    db.executescript('''
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            source_revision INTEGER NOT NULL,
            input_digest TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status = 'complete')
        );
        CREATE TABLE candidate_rows (
            run_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            cents INTEGER NOT NULL,
            PRIMARY KEY (run_id, event_id),
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        );
        CREATE TABLE selected (
            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
            generation INTEGER NOT NULL,
            run_id TEXT,
            source_revision INTEGER NOT NULL
        );
        INSERT INTO selected VALUES (1, 0, NULL, 0);
    ''')
    return db


def stage(db, run_id, source_revision, rows, expected_ids, fail_after=None):
    """Validate one complete synthetic source set, then stage it transactionally."""
    if type(run_id) is not str or not run_id or len(run_id) > 80:
        raise ValueError('Run ID must be a bounded nonempty string')
    if type(source_revision) is not int or source_revision <= 0:
        raise ValueError('Source revision must be a positive integer')
    rows, expected_ids = list(rows), list(expected_ids)
    if (not rows or any(type(event_id) is not str or not event_id or type(cents) is not int
                        or not -(2**63) <= cents < 2**63
                        for event_id, cents in rows)):
        raise ValueError('Rows need event IDs and signed 64-bit integer cents')
    actual_ids = [event_id for event_id, _ in rows]
    if (len(actual_ids) != len(set(actual_ids)) or len(expected_ids) != len(set(expected_ids))
            or set(actual_ids) != set(expected_ids)):
        raise ValueError('Candidate IDs must equal the declared expected source IDs')
    canonical = json.dumps([source_revision, sorted(rows), sorted(expected_ids)], separators=(',', ':'))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    old = db.execute('SELECT source_revision, input_digest FROM runs WHERE run_id = ?', (run_id,)).fetchone()
    if old is not None:
        if old != (source_revision, digest):
            raise ValueError('Run ID was reused with different input')
        return 'already_staged'
    with db:
        db.execute('INSERT INTO runs VALUES (?, ?, ?, ?)', (run_id, source_revision, digest, 'complete'))
        for index, (event_id, cents) in enumerate(rows, 1):
            db.execute('INSERT INTO candidate_rows VALUES (?, ?, ?)', (run_id, event_id, cents))
            if fail_after == index:
                raise RuntimeError('Synthetic worker failed before staging commit')
    return 'staged'


def publish(db, run_id, expected_generation):
    """Select a complete higher source revision with a local compare-and-swap."""
    if type(expected_generation) is not int or expected_generation < 0:
        raise ValueError('Expected generation must be a nonnegative integer')
    with db:
        current_generation, current_run, current_revision = db.execute(
            'SELECT generation, run_id, source_revision FROM selected WHERE singleton = 1').fetchone()
        if current_run == run_id:
            return 'already_current', current_generation
        if current_generation != expected_generation:
            return 'stale_generation', current_generation
        run = db.execute('SELECT source_revision FROM runs WHERE run_id = ? AND status = ?',
                         (run_id, 'complete')).fetchone()
        if run is None:
            return 'missing_complete_run', current_generation
        if run[0] <= current_revision:
            return 'stale_source_revision', current_generation
        changed = db.execute('''UPDATE selected SET generation = ?, run_id = ?, source_revision = ?
                                WHERE singleton = 1 AND generation = ?''',
                             (current_generation + 1, run_id, run[0], current_generation))
        if changed.rowcount != 1:
            raise RuntimeError('Local selection changed during transaction')
        return 'published', current_generation + 1


def current(db):
    generation, run_id, source_revision = db.execute(
        'SELECT generation, run_id, source_revision FROM selected WHERE singleton = 1').fetchone()
    rows = (db.execute('SELECT event_id, cents FROM candidate_rows WHERE run_id = ? ORDER BY event_id',
                       (run_id,)).fetchall() if run_id else [])
    return {'generation': generation, 'run_id': run_id,
            'source_revision': source_revision, 'rows': rows,
            'cents': sum(cents for _, cents in rows)}


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization so fixture assertions execute')
    db = open_store()
    assert stage(db, 'day1-v1', 1, [('a', 100), ('b', 200)], ['a', 'b']) == 'staged'
    assert publish(db, 'day1-v1', 0) == ('published', 1)
    first = current(db)
    assert first['cents'] == 300
    try:
        stage(db, 'day1-v2-failed', 2, [('a', 100), ('b', 200), ('late', 50)],
              ['a', 'b', 'late'], fail_after=1)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Injected failure did not stop staging')
    assert current(db) == first
    assert publish(db, 'day1-v2-failed', 1) == ('missing_complete_run', 1)
    assert stage(db, 'day1-v2', 2, [('a', 100), ('b', 200), ('late', 50)],
                 ['a', 'b', 'late']) == 'staged'
    assert publish(db, 'day1-v2', 1) == ('published', 2)
    second = current(db)
    assert second['cents'] == 350 and len(second['rows']) == 3
    assert stage(db, 'day1-v2', 2, [('late', 50), ('b', 200), ('a', 100)],
                 ['late', 'a', 'b']) == 'already_staged'
    assert publish(db, 'day1-v2', 2) == ('already_current', 2)
    assert publish(db, 'day1-v1', 2) == ('stale_source_revision', 2)
    assert current(db) == second
    print(json.dumps({'first': first, 'failed_stage_kept_first': True, 'second': second,
                      'rerun_did_not_double_total': True, 'older_run_rejected': True,
                      'scope': 'single in-memory SQLite store; not S3 object/catalog atomicity or source completeness'},
                     indent=2))
    db.close()


if __name__ == '__main__':
    main()
