"""Sequential local selective recovery; fictional authority, no AWS or application cutover."""
from contextlib import closing
from pathlib import Path
import json
import sqlite3
import sys
import tempfile


def snapshot(db, tenant=None):
    sql = 'SELECT tenant, id, amount FROM orders'
    params = ()
    if tenant is not None:
        sql += ' WHERE tenant=?'
        params = (tenant,)
    return list(db.execute(sql + ' ORDER BY tenant, id', params))


def repair(db, tenant, expected_current, desired, fail_after_delete=False):
    """Caller supplies a reviewed complete tenant state and its exact observed preimage.

    BEGIN IMMEDIATE excludes other SQLite writers while checking and replacing rows.
    Authentication, authority of desired state and distributed fencing are outside this model.
    """
    if any(row[0] != tenant for row in desired):
        raise ValueError('Recovery candidate includes another tenant')
    db.execute('BEGIN IMMEDIATE')
    try:
        if snapshot(db, tenant) != expected_current:
            raise ValueError('Stale recovery plan: tenant state changed')
        db.execute('DELETE FROM orders WHERE tenant=?', (tenant,))
        if fail_after_delete:
            raise RuntimeError('Injected interruption inside transaction')
        db.executemany('INSERT INTO orders VALUES (?,?,?)', desired)
        if snapshot(db, tenant) != sorted(desired):
            raise ValueError('Candidate reconciliation failed')
        db.commit()
    except Exception:
        db.rollback()
        raise


def copy(db, destination):
    with closing(sqlite3.connect(destination)) as dst:
        db.backup(dst)


def run(folder):
    live_path = folder / 'live.sqlite'
    backup_path = folder / 'historical.sqlite'
    unsafe_path = folder / 'unsafe-restored.sqlite'
    with closing(sqlite3.connect(live_path)) as db:
        db.execute('CREATE TABLE orders (tenant TEXT NOT NULL, id TEXT NOT NULL, '
                   'amount INTEGER NOT NULL CHECK(amount>0), PRIMARY KEY(tenant,id))')
        db.executemany('INSERT INTO orders VALUES (?,?,?)', [('A','1',100),('B','1',200)])
        db.commit()
        copy(db, backup_path)
        # Same local ID in each tenant forces us to preserve the composite key.
        db.execute("UPDATE orders SET amount=250 WHERE tenant='B' AND id='1'")
        db.execute("INSERT INTO orders VALUES ('B','2',300)")
        db.execute("INSERT INTO orders VALUES ('A','2',150)")
        db.commit()
        confirmed_a = snapshot(db, 'A')  # fictional independent authority captured before damage
        current_b = snapshot(db, 'B')
        db.execute("DELETE FROM orders WHERE tenant='A' AND id='1'")
        db.commit()
        damaged = snapshot(db)
        observed_a = snapshot(db, 'A')
        with closing(sqlite3.connect(backup_path)) as historical:
            historical_before = snapshot(historical)
            copy(historical, unsafe_path)
            old_a = snapshot(historical, 'A')
        with closing(sqlite3.connect(unsafe_path)) as unsafe:
            assert snapshot(unsafe, 'B') == [('B','1',200)]
            assert snapshot(unsafe, 'B') != current_b  # loses B2 and reverses B1's amount
            assert snapshot(unsafe, 'A') != confirmed_a  # loses confirmed A2 as well
        assert old_a != confirmed_a
        # Restoring only historical A would still lose its later confirmed order.
        assert set(confirmed_a) - set(old_a) == {('A','2',150)}
        try:
            repair(db, 'A', observed_a, confirmed_a, fail_after_delete=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Injected failure was not raised')
        assert snapshot(db) == damaged  # DELETE rolled back; B also unchanged
        try:
            repair(db, 'A', observed_a, confirmed_a + [('B','1',200)])
        except ValueError:
            pass
        else:
            raise AssertionError('Cross-tenant candidate accepted')
        assert snapshot(db) == damaged
        # A legitimate post-plan update makes the recovery plan stale.
        db.execute("UPDATE orders SET amount=175 WHERE tenant='A' AND id='2'")
        db.commit()
        after_new_write = snapshot(db)
        try:
            repair(db, 'A', observed_a, confirmed_a)
        except ValueError as error:
            assert 'Stale recovery plan' in str(error)
        else:
            raise AssertionError('Stale recovery plan accepted')
        assert snapshot(db) == after_new_write
        # A reviewed ledger revision includes the legitimate amount change.
        revised_authority = [('A','1',100),('A','2',175)]
        repair(db, 'A', snapshot(db, 'A'), revised_authority)
        assert snapshot(db, 'A') == revised_authority
        assert snapshot(db, 'B') == current_b
        repaired = snapshot(db)
        repair(db, 'A', snapshot(db, 'A'), revised_authority)
        assert snapshot(db) == repaired  # repeated repair preserves exact state
        with closing(sqlite3.connect(backup_path)) as historical:
            assert snapshot(historical) == historical_before
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        return {'unsafe_whole_restore': 'reverses B1; loses B2 and A2',
                'historical_A_only': 'missing later confirmed A2',
                'interrupted_transaction': 'all original rows preserved',
                'cross_tenant_candidate': 'rejected without changes',
                'stale_plan': 'rejected without changes',
                'repaired_A': snapshot(db, 'A'), 'preserved_B': snapshot(db, 'B'),
                'repeat_repair': 'exact rows unchanged',
                'scope': 'Actual sequential SQLite transactions; fictional complete ledger; '
                         'no concurrent-writer test, AWS recovery, files, external effects or live cutover'}


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Run without -O')
    with tempfile.TemporaryDirectory(prefix='amplify-tenant-recovery-') as tmp:
        folder = Path(tmp)
        result = run(folder)
    result['temporary_resources_removed'] = not folder.exists()
    assert result['temporary_resources_removed']
    print(json.dumps(result, indent=2))
