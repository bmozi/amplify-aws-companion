"""Decision-relevant failure and retry cases for the local reverse replay."""

from pathlib import Path
import sqlite3
import tempfile
import unittest

from lab import old_rows, return_to_source_if_reconciled
from reverse_lab import ReplayConflict, ReplayInterrupted, fixture, replay_target_to_source


class ReverseReplayTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source, self.target, self.pointer = fixture(Path(self.temporary.name))

    def test_interruption_preserves_old_source_and_target_authority(self):
        with self.assertRaises(ReplayInterrupted):
            replay_target_to_source(self.source, self.target, fail_after=1)
        self.assertEqual(old_rows(self.source), [('a', '12.99')])
        self.assertFalse(return_to_source_if_reconciled(self.source, self.target, self.pointer))
        self.assertEqual(self.pointer.read_text(), self.target.name)

    def test_replay_is_idempotent_then_local_return_can_pass(self):
        self.assertEqual(replay_target_to_source(self.source, self.target), 2)
        self.assertEqual(replay_target_to_source(self.source, self.target), 0)
        self.assertTrue(return_to_source_if_reconciled(self.source, self.target, self.pointer))
        self.assertEqual(old_rows(self.source),
                         [('a', '12.99'), ('e', '2.50'), ('f', '3.75')])

    def test_conflict_refuses_overwrite_and_preserves_pointer(self):
        with sqlite3.connect(self.source) as db:
            db.execute('INSERT INTO orders VALUES (?,?)', ('e', '9.99'))
        with self.assertRaisesRegex(ReplayConflict, 'e'):
            replay_target_to_source(self.source, self.target)
        self.assertEqual(old_rows(self.source), [('a', '12.99'), ('e', '9.99')])
        self.assertFalse(return_to_source_if_reconciled(self.source, self.target, self.pointer))
        self.assertEqual(self.pointer.read_text(), self.target.name)


if __name__ == '__main__':
    unittest.main()
