"""Changed-state and failure controls for the local migration replay."""

from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from versioned_return_lab import (ChangeConflict, ReplayInterrupted, apply,
                                  guarded_return, journal, replay, rows, setup)


class VersionedReturnTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.source, self.target, self.pointer = setup(Path(temporary.name))

    def test_interruption_rolls_back_all_changes_then_retry_is_idempotent(self):
        with self.assertRaises(ReplayInterrupted):
            replay(self.source, self.target, fail_after=2)
        with closing(sqlite3.connect(self.source)) as old:
            self.assertEqual(journal(old), [])
            self.assertEqual(rows(old), [('e', 250, 1, 0), ('f', 375, 1, 0)])
        self.assertFalse(guarded_return(self.source, self.target, self.pointer))
        self.assertEqual(self.pointer.read_text(), self.target.name)
        self.assertEqual(replay(self.source, self.target), 3)
        self.assertEqual(replay(self.source, self.target), 0)
        self.assertTrue(guarded_return(self.source, self.target, self.pointer))
        with closing(sqlite3.connect(self.source)) as old:
            self.assertEqual(rows(old), [('e', 300, 2, 0), ('f', 375, 2, 1),
                                         ('g', 425, 1, 0)])

    def test_same_revision_but_changed_old_amount_refuses_and_rolls_back(self):
        with closing(sqlite3.connect(self.source)) as old, old:
            old.execute("UPDATE orders SET amount_cents=999 WHERE id='e'")
        with self.assertRaisesRegex(ChangeConflict, 'old value'):
            replay(self.source, self.target)
        with closing(sqlite3.connect(self.source)) as old:
            self.assertEqual(journal(old), [])
            self.assertEqual(rows(old)[0], ('e', 999, 1, 0))
        self.assertFalse(guarded_return(self.source, self.target, self.pointer))

    def test_stale_revision_refuses_without_erasing_old_write(self):
        with closing(sqlite3.connect(self.source)) as old, old:
            old.execute("UPDATE orders SET amount_cents=999,revision=2 WHERE id='e'")
        with self.assertRaisesRegex(ChangeConflict, 'revision'):
            replay(self.source, self.target)
        with closing(sqlite3.connect(self.source)) as old:
            self.assertEqual(rows(old)[0], ('e', 999, 2, 0))
        self.assertEqual(self.pointer.read_text(), self.target.name)

    def test_tombstone_and_journal_are_both_required(self):
        self.assertEqual(replay(self.source, self.target), 3)
        with closing(sqlite3.connect(self.source)) as old, old:
            old.execute("DELETE FROM orders WHERE id='f'")
        self.assertFalse(guarded_return(self.source, self.target, self.pointer))
        with closing(sqlite3.connect(self.source)) as old, old:
            old.execute('INSERT INTO orders VALUES (?,?,?,?)', ('f', 375, 2, 1))
            old.execute('DELETE FROM changes WHERE sequence=2')
        self.assertFalse(guarded_return(self.source, self.target, self.pointer))

    def test_divergent_journal_blocks_retry_even_if_values_match(self):
        self.assertEqual(replay(self.source, self.target), 3)
        with closing(sqlite3.connect(self.source)) as old, old:
            old.execute("UPDATE changes SET amount_cents=301 WHERE sequence=1")
        with self.assertRaisesRegex(ChangeConflict, 'not a prefix'):
            replay(self.source, self.target)
        self.assertFalse(guarded_return(self.source, self.target, self.pointer))

    def test_deleted_id_cannot_be_recreated_as_a_new_order(self):
        with closing(sqlite3.connect(self.target)) as db:
            with self.assertRaisesRegex(ChangeConflict, 'tombstone'):
                apply(db, (4, 'f', 0, None, 'create', 500))
            self.assertEqual(rows(db)[1], ('f', 375, 2, 1))


if __name__ == '__main__':
    unittest.main()
