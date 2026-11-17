"""Two-connection SQLite demonstration of a late old writer during schema expansion."""

from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile


def rows(db):
    return db.execute("SELECT id, email, contact_email FROM customers ORDER BY id").fetchall()


def mismatches(db):
    return db.execute("SELECT id FROM customers WHERE contact_email IS NULL OR email != contact_email ORDER BY id").fetchall()


def run():
    with tempfile.TemporaryDirectory(prefix="amplify-schema-overlap-") as directory:
        path = Path(directory) / "customers.sqlite"
        with closing(sqlite3.connect(path, isolation_level=None)) as new, closing(sqlite3.connect(path, isolation_level=None)) as old:
            new.execute("CREATE TABLE customers(id INTEGER PRIMARY KEY, email TEXT NOT NULL, contact_email TEXT)")
            new.execute("CREATE TABLE migration_control(id INTEGER PRIMARY KEY CHECK(id=1), phase TEXT NOT NULL)")
            new.execute("INSERT INTO migration_control VALUES (1, 'expanded')")
            new.execute("INSERT INTO customers VALUES (1, 'first@example.test', NULL)")
            new.execute("UPDATE customers SET contact_email=email")
            assert mismatches(new) == []

            # This is the tempting but insufficient check-before-cutover.
            checked_before_late_write = mismatches(new)
            old.execute("UPDATE customers SET email=? WHERE id=1", ("late@example.test",))
            assert checked_before_late_write == [] and mismatches(new) == [(1,)]
            assert rows(old) == [(1, "late@example.test", "first@example.test")]

            new.execute("UPDATE customers SET contact_email=email")
            new.execute("""CREATE TRIGGER reject_legacy_only_write
                BEFORE UPDATE ON customers
                WHEN (SELECT phase FROM migration_control WHERE id=1)='fenced'
                     AND NEW.email IS NOT NEW.contact_email
                BEGIN SELECT RAISE(ABORT, 'legacy-only write blocked'); END""")
            assert mismatches(new) == []
            old_observed_phase = old.execute("SELECT phase FROM migration_control WHERE id=1").fetchone()[0]
            assert old_observed_phase == "expanded"

            # SQLite serializes writes. The final check and phase change share
            # one write transaction; a stale old process still reaches the trigger.
            new.execute("BEGIN IMMEDIATE")
            try:
                assert mismatches(new) == []
                new.execute("UPDATE migration_control SET phase='fenced' WHERE id=1")
                new.execute("COMMIT")
            except BaseException:
                new.execute("ROLLBACK")
                raise
            before_rejected_write = rows(new)
            try:
                old.execute("UPDATE customers SET email=? WHERE id=1", ("too-late@example.test",))
            except sqlite3.IntegrityError as error:
                assert "legacy-only write blocked" in str(error)
            else:
                raise AssertionError("old-only write passed the current database gate")
            assert rows(new) == before_rejected_write

            # The compatible writer changes both representations in one SQL
            # statement; two separate UPDATEs would violate the immediate guard.
            new.execute("UPDATE customers SET email=?, contact_email=? WHERE id=1",
                        ("current@example.test", "current@example.test"))
            assert rows(new) == [(1, "current@example.test", "current@example.test")]
            new.execute("BEGIN")
            try:
                new.execute("UPDATE customers SET email=? WHERE id=1", ("split@example.test",))
            except sqlite3.IntegrityError as error:
                assert "legacy-only write blocked" in str(error)
                new.execute("ROLLBACK")
            else:
                new.execute("ROLLBACK")
                raise AssertionError("two-statement writer passed the immediate guard")
            assert rows(new) == [(1, "current@example.test", "current@example.test")]
            assert mismatches(old) == []
            return {
                "pre_fence_clean_check": checked_before_late_write,
                "late_old_write_created_mismatch": [1],
                "old_phase_read_before_fence": old_observed_phase,
                "old_write_after_fence": "rejected without changing the row",
                "compatible_single_statement_write": "accepted",
                "compatible_two_statement_write": "first statement rejected and rolled back",
                "final_row": rows(new),
                "scope": "two SQLite connections; no distributed writer inventory, AWS database, or zero-downtime claim",
            }


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    print(json.dumps(run(), indent=2))
