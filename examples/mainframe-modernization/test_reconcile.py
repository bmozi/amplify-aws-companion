"""Check that the teaching gate catches material business-output defects."""

import tempfile
import unittest
from pathlib import Path

from reconcile import compare, load

HERE = Path(__file__).resolve().parent


class ReconcileTest(unittest.TestCase):
    def test_synthetic_match_and_held_claim_defect(self):
        self.assertEqual(compare(HERE / "source.csv", HERE / "candidate.csv"), [])
        self.assertIn("C-102", " ".join(compare(HERE / "source.csv", HERE / "candidate-defect.csv")))

    def test_missing_and_duplicate_records_do_not_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.csv"
            path.write_text("claim_id,amount_cents,status\nC-101,12500,PAID\n")
            self.assertIn("missing claim C-102", compare(HERE / "source.csv", path))
            path.write_text("claim_id,amount_cents,status\nC-101,12500,PAID\nC-101,12500,PAID\n")
            with self.assertRaisesRegex(ValueError, "duplicate claim ID"):
                load(path)


if __name__ == "__main__":
    unittest.main()
