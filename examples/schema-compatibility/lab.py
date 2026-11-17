"""Actual SQLite schema changes; sequential teaching schedule, no cloud deployment."""
from contextlib import closing
import json
import sqlite3


def old_read(db):
    return db.execute('SELECT id,email FROM customers ORDER BY id').fetchall()


def new_read(db):
    return db.execute('SELECT id,COALESCE(contact_email,email) FROM customers ORDER BY id').fetchall()


def mismatches(db):
    return db.execute('SELECT id FROM customers WHERE contact_email IS NULL OR contact_email != email ORDER BY id').fetchall()


def compatible_write(db, value, fail=False):
    db.execute('BEGIN')
    try:
        db.execute('UPDATE customers SET email=? WHERE id=1', (value,))
        if fail:
            raise RuntimeError('injected between representations')
        db.execute('UPDATE customers SET contact_email=? WHERE id=1', (value,))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK')
        raise


def run():
    with closing(sqlite3.connect(':memory:', isolation_level=None)) as db:
        db.execute('CREATE TABLE customers(id INTEGER PRIMARY KEY,email TEXT NOT NULL)')
        db.execute("INSERT INTO customers VALUES (1,'first@example.test')")
        assert old_read(db)==[(1,'first@example.test')]
        db.execute('ALTER TABLE customers ADD COLUMN contact_email TEXT')
        assert new_read(db)==old_read(db)
        db.execute('UPDATE customers SET contact_email=email')
        assert mismatches(db)==[]
        # Old writer still exists after the first backfill.
        db.execute("UPDATE customers SET email='changed@example.test' WHERE id=1")
        stale=new_read(db)
        assert stale==[(1,'first@example.test')]
        assert old_read(db)==[(1,'changed@example.test')]
        assert mismatches(db)==[(1,)], 'old writer must block contraction'
        # Fixture now retires old-only writers. Real systems need a verified fence.
        db.execute('UPDATE customers SET contact_email=email')
        assert new_read(db)==old_read(db)==[(1,'changed@example.test')]
        compatible_write(db,'compatible@example.test')
        assert new_read(db)==old_read(db)==[(1,'compatible@example.test')]
        try:
            compatible_write(db,'uncommitted@example.test',fail=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError('failure injection did not occur')
        assert new_read(db)==old_read(db)==[(1,'compatible@example.test')]
        assert mismatches(db)==[]
        # Contract by transactional table replacement, retaining the new representation.
        db.execute('BEGIN')
        try:
            db.execute('CREATE TABLE replacement(id INTEGER PRIMARY KEY,contact_email TEXT NOT NULL)')
            db.execute('INSERT INTO replacement SELECT id,contact_email FROM customers')
            db.execute('DROP TABLE customers')
            db.execute('ALTER TABLE replacement RENAME TO customers')
            db.execute('COMMIT')
        except BaseException:
            db.execute('ROLLBACK')
            raise
        assert db.execute('SELECT id,contact_email FROM customers').fetchall()==[(1,'compatible@example.test')]
        try:
            old_read(db)
        except sqlite3.OperationalError as error:
            assert 'no such column' in str(error)
        else:
            raise AssertionError('old reader unexpectedly survived contraction')
        # The compatibility reader also refers to email; deploy a new-only reader first.
        try:
            new_read(db)
        except sqlite3.OperationalError as error:
            assert 'no such column' in str(error)
        else:
            raise AssertionError('fallback reader unexpectedly survived contraction')
        return {'expanded_old_and_new_readers':'passed', 'old_writer_detected':stale,
                'atomic_write_rollback':'passed', 'new_only_read_after_contract':'passed',
                'old_and_fallback_readers_after_contract':'rejected',
                'scope':'sequential SQLite; no live writer fencing or AWS migration'}


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    print(json.dumps(run(),indent=2))
