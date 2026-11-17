import tempfile
import unittest
from pathlib import Path

from closure_race import ClosureRace, demonstrate


class ClosureRaceTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.case = ClosureRace(Path(self.folder.name))

    def tearDown(self):
        self.folder.cleanup()

    def test_split_check_becomes_stale_before_data_read(self):
        self.assertEqual(self.case.split_read_with_closure_between(), "private note")
        with self.assertRaises(PermissionError):
            self.case.split_read_with_closure_between()

    def test_one_file_transaction_orders_read_before_close(self):
        self.assertEqual(self.case.joined_read_with_close_attempt(), ("private note", True))
        self.case.close_joined_after_read()
        with self.assertRaises(PermissionError):
            self.case.joined_read_after_close()

    def test_receipt(self):
        result = demonstrate()
        self.assertTrue(result["split_check_then_close_then_read_leaks_note"])
        self.assertTrue(result["joined_close_blocked_during_read"])
        self.assertTrue(result["joined_read_after_close_denied"])


if __name__ == "__main__":
    unittest.main()
