import importlib.util
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("a21_failback", Path(__file__).with_name("failback_lab.py"))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class FailbackLabTests(unittest.TestCase):
    def test_return_requires_reverse_receipts_and_closed_old_writer(self):
        result = lab.run()
        self.assertEqual(result["forward"], "READY")
        self.assertEqual(result["stale_return"]["missing_confirmed"], ["r-bob"])
        self.assertEqual(result["premature_reverse"], "NO_GO_WRITER_OPEN")
        self.assertEqual(result["reverse"], "READY")
        self.assertEqual(result["safe_return"]["visible"], ["r-alice", "r-bob"])
        self.assertTrue(result["safe_return"]["old_writer_closed"])

    def test_missing_receipt_and_open_writer_stop_handoff(self):
        with tempfile.TemporaryDirectory() as folder:
            source = lab.Store(Path(folder) / "a.sqlite", "a")
            target = lab.Store(Path(folder) / "b.sqlite", "b")
            try:
                source.writer_open = True
                self.assertEqual(source.book("r1", "09:00", "Alice"), "ACCEPTED")
                self.assertEqual(lab.copy_and_check(source, target, {"r1"}), "NO_GO_WRITER_OPEN")
                source.writer_open = False
                self.assertEqual(lab.copy_and_check(source, target, set()), "NO_GO_MISSING_SOURCE_RECEIPT")
                self.assertEqual(lab.copy_and_check(source, target, {"r1"}), "READY")
            finally:
                source.close()
                target.close()

    def test_same_slot_conflict_does_not_claim_complete_handoff(self):
        with tempfile.TemporaryDirectory() as folder:
            source = lab.Store(Path(folder) / "a.sqlite", "a")
            target = lab.Store(Path(folder) / "b.sqlite", "b")
            try:
                source.writer_open = True
                target.writer_open = True
                self.assertEqual(source.book("r1", "09:00", "Alice"), "ACCEPTED")
                self.assertEqual(target.book("r2", "09:00", "Bob"), "ACCEPTED")
                source.writer_open = target.writer_open = False
                self.assertEqual(lab.copy_and_check(source, target, {"r1"}), "NO_GO_MISMATCH")
                self.assertEqual(target.rows(), [("r2", "09:00", "Bob")])
            finally:
                source.close()
                target.close()


if __name__ == "__main__":
    unittest.main()
