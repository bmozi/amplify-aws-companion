"""Recover local business data and identify confirmed writes missing from a backup. No AWS calls."""
from pathlib import Path
from contextlib import contextmanager, closing
import json
import sqlite3
import sys
import tempfile
import time


@contextmanager
def database(path):
    # sqlite3's transaction context commits/rolls back but does not close the connection.
    with closing(sqlite3.connect(path)) as db:
        with db:
            yield db


def maintained_copy_scenario(folder, good_source):
    writer, reader, history, candidate = [folder / name for name in
        ('copy-writer.sqlite', 'maintained-copy.sqlite', 'history.sqlite', 'history-restored.sqlite')]
    copy_database(good_source, writer)
    copy_database(writer, reader)
    copy_database(writer, history)
    earlier = records(history)
    assert earlier == {'order-1': 1200, 'order-2': 2300, 'order-3': 900}
    with database(writer) as db:
        db.execute('INSERT INTO orders VALUES (?,?)', ('order-4', 500))
    assert 'order-4' not in records(reader)  # controlled delay before refreshing the copy
    confirmed = {**earlier, 'order-4': 500}
    assert records(writer) == confirmed
    copy_database(writer, reader)
    assert records(reader) == confirmed
    with database(writer) as db:
        db.execute('DELETE FROM orders WHERE id=?', ('order-2',))
    copy_database(writer, reader)  # full local refresh intentionally copies the deletion too
    assert records(reader) == records(writer) == {'order-1': 1200, 'order-3': 900, 'order-4': 500}
    assert reconcile(records(reader), confirmed) == {'missing': ['order-2'], 'unexpected': [], 'changed': []}
    assert records(history) == earlier
    copy_database(history, candidate)
    before = reconcile(records(candidate), confirmed)
    assert before == {'missing': ['order-4'], 'unexpected': [], 'changed': []}
    with database(candidate) as db:
        db.execute('INSERT INTO orders VALUES (?,?)', ('order-4', confirmed['order-4']))
    assert records(candidate) == confirmed
    assert sum(records(candidate).values()) == 4900
    assert 'order-2' not in records(writer)  # separate recovery; no automatic production cutover
    return {'maintained_copy_missing': ['order-2'], 'history_missing_before_replay': before['missing'],
            'recovered_total_cents': 4900,
            'scope': 'Full local SQLite copy refresh; not engine replication, CDC, promotion or measured lag'}


def records(path):
    with database(path) as db:
        return dict(db.execute('SELECT id, amount_cents FROM orders ORDER BY id'))


def copy_database(source, destination):
    with database(source) as src, database(destination) as dst:
        src.backup(dst)


def reconcile(actual, confirmed):
    return {
        'missing': sorted(set(confirmed) - set(actual)),
        'unexpected': sorted(set(actual) - set(confirmed)),
        'changed': sorted(k for k in set(actual) & set(confirmed) if actual[k] != confirmed[k]),
    }


def run(folder):
    source = folder / 'source.sqlite'
    backup = folder / 'backup.sqlite'
    bad_backup = folder / 'bad-backup.sqlite'
    restored = folder / 'restored.sqlite'
    # Synthetic event timestamps describe a fictional incident, not wall-clock AWS timing.
    events = [('order-1', 1200, 0), ('order-2', 2300, 60), ('order-3', 900, 180)]
    with database(source) as db:
        db.execute('CREATE TABLE orders (id TEXT PRIMARY KEY, amount_cents INTEGER NOT NULL CHECK(amount_cents > 0))')
        db.executemany('INSERT INTO orders VALUES (?,?)', [(i, amount) for i, amount, _ in events[:2]])
    copy_database(source, backup)  # recovery point at fictional second 60
    with database(source) as db:
        db.execute('INSERT INTO orders VALUES (?,?)', events[2][:2])
    confirmed = {i: amount for i, amount, _ in events}
    assert records(source) == confirmed
    copy_database(source, bad_backup)
    with database(bad_backup) as db:
        db.execute('UPDATE orders SET amount_cents=1 WHERE id=?', ('order-2',))
    # A newer backup may be structurally valid and have the correct count yet wrong content.
    with database(bad_backup) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    bad = records(bad_backup)
    assert len(bad) == len(confirmed)
    bad_diff = reconcile(bad, confirmed)
    assert bad_diff == {'missing': [], 'unexpected': [], 'changed': ['order-2']}
    # Equal count and total can still conceal the wrong business identity.
    substituted = {'order-1': 1200, 'order-2': 2300, 'order-X': 900}
    assert len(substituted) == len(confirmed) and sum(substituted.values()) == sum(confirmed.values())
    substitution_diff = reconcile(substituted, confirmed)
    assert substitution_diff == {'missing': ['order-3'], 'unexpected': ['order-X'], 'changed': []}
    started = time.perf_counter()
    copy_database(backup, restored)
    before = reconcile(records(restored), confirmed)
    assert before == {'missing': ['order-3'], 'unexpected': [], 'changed': []}
    # Recovery authority is the independent synthetic confirmed-event ledger.
    # Do not infer missing orders from the damaged database or invent them.
    with database(restored) as db:
        for key in before['missing']:
            db.execute('INSERT INTO orders VALUES (?,?)', (key, confirmed[key]))
    after = reconcile(records(restored), confirmed)
    assert after == {'missing': [], 'unexpected': [], 'changed': []}
    assert sum(records(restored).values()) == 4400
    # Repeating reconciliation must not create duplicates or change content.
    assert reconcile(records(restored), confirmed) == after
    with database(restored) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert records(source) == confirmed  # no overwrite or cutover of original database
    return {
        'newer_backup': {'integrity': 'ok', 'count_matches': True, 'reconciliation': bad_diff, 'accepted': False},
        'equal_count_and_total_wrong_identity': {'reconciliation': substitution_diff, 'accepted': False},
        'older_backup': {'reconciliation_before_replay': before, 'reconciliation_after_replay': after},
        'fictional_timeline_seconds': {'backup_recovery_point': 60, 'last_confirmed_write': 180, 'incident': 240},
        'backup_only_exposure_window_seconds': 180,
        'missing_confirmed_order_count_before_replay': 1,
        'recovered_total_cents': 4400,
        'local_restore_and_validation_seconds': time.perf_counter() - started,
        'scope': 'Actual local SQLite restore and reconciliation; synthetic times and independent event ledger; no AWS RTO/RPO measurement or service cutover',
    }


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without -O')
    with tempfile.TemporaryDirectory(prefix='amplify-recovery-') as temporary:
        folder = Path(temporary)
        result = run(folder)
        result['maintained_copy_scenario'] = maintained_copy_scenario(folder, folder / 'restored.sqlite')
    result['temporary_resources_removed'] = not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result, indent=2))
