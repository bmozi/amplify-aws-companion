"""Local two-writer selection for immutable report files; no AWS calls."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier

import file_publication_lab as files


def connect(path):
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.execute('PRAGMA busy_timeout = 5000')
    return db


def initialize(path):
    with closing(connect(path)) as db:
        db.execute('CREATE TABLE selection (singleton INTEGER PRIMARY KEY CHECK (singleton = 1), '
                   'generation INTEGER NOT NULL, run_id TEXT NOT NULL, source_revision INTEGER NOT NULL)')
        db.execute("INSERT INTO selection VALUES (1, 1, 'v1', 1)")


def selection(db):
    generation, run_id, revision = db.execute(
        'SELECT generation, run_id, source_revision FROM selection WHERE singleton = 1').fetchone()
    return {'generation': generation, 'run_id': run_id, 'source_revision': revision}


def publish(db_path, root, run_id, expected_generation, ready=None):
    """One local database transaction selects one already-complete file set."""
    if type(expected_generation) is not int or expected_generation < 0:
        raise ValueError('Expected generation must be nonnegative')
    if ready is not None:
        ready.wait(timeout=5)
    db = connect(db_path)
    try:
        db.execute('BEGIN IMMEDIATE')
        prior = selection(db)
        if prior['run_id'] == run_id:
            files.candidate(root, run_id)
            result = ('already_current', prior['generation'])
        elif prior['generation'] != expected_generation:
            result = ('stale_generation', prior['generation'])
        elif not (files.run_path(root, run_id) / 'manifest.json').exists():
            result = ('missing_complete_run', prior['generation'])
        else:
            manifest, _ = files.candidate(root, run_id)
            if manifest['source_revision'] <= prior['source_revision']:
                result = ('stale_source_revision', prior['generation'])
            else:
                changed = db.execute(
                    'UPDATE selection SET generation = ?, run_id = ?, source_revision = ? '
                    'WHERE singleton = 1 AND generation = ?',
                    (prior['generation'] + 1, run_id, manifest['source_revision'],
                     prior['generation']))
                if changed.rowcount != 1:
                    raise AssertionError('Selection changed inside the local write transaction')
                result = ('published', prior['generation'] + 1)
        db.commit()
        return result
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def read_view(db_path, root):
    with closing(connect(db_path)) as db:
        pointer = selection(db)
    return files.read_view(root, pointer)


def staged_fixture(root):
    files.stage(root, 'v1', 1, [[('a', 100), ('b', 200)], []], ['a', 'b'])
    files.stage(root, 'v2', 2, [[('a', 100), ('b', 180)], [('late', 50)]],
                ['a', 'b', 'late'])
    files.stage(root, 'v3', 3, [[('a', 100), ('b', 190)], [('late', 50)]],
                ['a', 'b', 'late'])


def race(root, db_path):
    ready = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(publish, db_path, root, 'v2', 1, ready)
        b = pool.submit(publish, db_path, root, 'v3', 1, ready)
        return {'v2': a.result(timeout=10), 'v3': b.result(timeout=10)}


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        staged_fixture(root)
        db_path = root / 'selection.sqlite3'
        initialize(db_path)
        outcomes = race(root, db_path)
        view = read_view(db_path, root)
        assert sorted(result[0] for result in outcomes.values()) == ['published', 'stale_generation']
        assert view['pointer']['generation'] == 2
        assert view['cents'] == {'v2': 330, 'v3': 340}[view['pointer']['run_id']]
        assert outcomes[view['pointer']['run_id']] == ('published', 2)
        print(json.dumps({'outcomes': outcomes, 'selected': view,
                          'scope': 'two local threads, independent SQLite connections and local files; '
                                   'not distributed S3/Glue/Athena selection'}, indent=2))


if __name__ == '__main__':
    main()
