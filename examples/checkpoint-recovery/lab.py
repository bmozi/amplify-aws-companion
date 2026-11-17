"""Actual local worker exits and restarts across separate SQLite commits; no AWS."""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

CRASH_EXIT = 73
CONFLICT_EXIT = 74
EVENTS = [{'id': 'sale-a', 'cents': 1000}, {'id': 'sale-b', 'cents': 2000}]


def prepare(root):
    root.mkdir()
    (root/'source.json').write_text(json.dumps(EVENTS))
    with closing(sqlite3.connect(root/'effects.db')) as db:
        db.executescript('CREATE TABLE ledger (id TEXT PRIMARY KEY, body TEXT NOT NULL); '
                         'CREATE TABLE total (singleton INTEGER PRIMARY KEY CHECK(singleton=1), cents INTEGER NOT NULL); '
                         'INSERT INTO total VALUES (1,0);')
    with closing(sqlite3.connect(root/'progress.db')) as db:
        db.executescript('CREATE TABLE progress (singleton INTEGER PRIMARY KEY CHECK(singleton=1), position INTEGER NOT NULL); '
                         'INSERT INTO progress VALUES (1,0);')


def position(root):
    with closing(sqlite3.connect(root/'progress.db')) as db:
        return db.execute('SELECT position FROM progress WHERE singleton=1').fetchone()[0]


def checkpoint(root, number):
    with closing(sqlite3.connect(root/'progress.db')) as db, db:
        db.execute('UPDATE progress SET position=? WHERE singleton=1', (number,))


def effect(root, event):
    # Identity receipt and counter update share one destination transaction.
    body = json.dumps(event, sort_keys=True, separators=(',', ':'))
    with closing(sqlite3.connect(root/'effects.db')) as db, db:
        db.execute('BEGIN IMMEDIATE')
        prior = db.execute('SELECT body FROM ledger WHERE id=?', (event['id'],)).fetchone()
        if prior:
            if prior[0] != body:
                raise ValueError('Same business identity with different content')
            return 'duplicate'
        db.execute('INSERT INTO ledger VALUES (?,?)', (event['id'], body))
        db.execute('UPDATE total SET cents=cents+? WHERE singleton=1', (event['cents'],))
    return 'created'


def state(root):
    with closing(sqlite3.connect(root/'effects.db')) as db:
        ids = [r[0] for r in db.execute('SELECT id FROM ledger ORDER BY id')]
        cents = db.execute('SELECT cents FROM total WHERE singleton=1').fetchone()[0]
    return {'position': position(root), 'ids': ids, 'cents': cents}


def worker(root, strategy, fault):
    # Source file and payloads are trusted fixtures, not an authenticated stream.
    events = json.loads((root/'source.json').read_text())
    start = position(root)
    outcomes = []
    for number, event in enumerate(events, 1):
        if number <= start:
            continue
        if strategy == 'progress-first':
            checkpoint(root, number)
            if fault == 'after-progress':
                os._exit(CRASH_EXIT)  # Skip Python cleanup after the committed write.
        outcome = effect(root, event)
        if fault == 'after-effect':
            os._exit(CRASH_EXIT)
        if strategy == 'effect-first':
            checkpoint(root, number)
        outcomes.append({'position': number, 'outcome': outcome})
    return outcomes


def launch(root, strategy='effect-first', fault='none', expected=0):
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker', str(root),
                             '--strategy', strategy, '--fault', fault], capture_output=True,
                            text=True, timeout=15)
    assert result.returncode == expected, (result.returncode, result.stdout, result.stderr)
    return json.loads(result.stdout) if result.stdout else None


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    with tempfile.TemporaryDirectory(prefix='amplify-checkpoint-') as temporary:
        root = Path(temporary)
        early, late = root/'early', root/'late'
        prepare(early)
        launch(early, strategy='progress-first', fault='after-progress', expected=CRASH_EXIT)
        assert state(early) == {'position': 1, 'ids': [], 'cents': 0}
        launch(early, strategy='progress-first')
        early_result = state(early)
        assert early_result == {'position': 2, 'ids': ['sale-b'], 'cents': 2000}

        prepare(late)
        launch(late, fault='after-effect', expected=CRASH_EXIT)
        assert state(late) == {'position': 0, 'ids': ['sale-a'], 'cents': 1000}
        replay = launch(late)
        assert replay == [{'position': 1, 'outcome': 'duplicate'}, {'position': 2, 'outcome': 'created'}]
        final = state(late)
        assert final == {'position': 2, 'ids': ['sale-a','sale-b'], 'cents': 3000}
        assert launch(late) == []
        assert state(late) == final

        # A producer retry at a new source position still has the same business identity.
        (late/'source.json').write_text(json.dumps(EVENTS + [EVENTS[0]]))
        assert launch(late) == [{'position': 3, 'outcome': 'duplicate'}]
        assert state(late) == dict(final, position=3)
        conflict = {'id': 'sale-a', 'cents': 9999}
        (late/'source.json').write_text(json.dumps(EVENTS + [EVENTS[0], conflict]))
        assert launch(late, expected=CONFLICT_EXIT) == {'error': 'conflicting business identity'}
        assert state(late) == dict(final, position=3)
        print(json.dumps({'progress_first_lost_effect': early_result,
                          'effect_first_restart': final, 'restart_outcomes': replay,
                          'producer_duplicate_position': 3, 'conflict_did_not_advance': True,
                          'scope': 'Real local process exits and SQLite persistence; fictional source positions; no AWS or concurrent consumer protocol'}, indent=2))
    assert not root.exists()
    print('Removed temporary source, ledger and checkpoint files.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', type=Path)
    parser.add_argument('--strategy', choices=['progress-first','effect-first'], default='effect-first')
    parser.add_argument('--fault', choices=['none','after-progress','after-effect'], default='none')
    args = parser.parse_args()
    if args.worker:
        try:
            print(json.dumps(worker(args.worker, args.strategy, args.fault)))
        except ValueError:
            print(json.dumps({'error': 'conflicting business identity'}))
            raise SystemExit(CONFLICT_EXIT)
    else:
        main()
