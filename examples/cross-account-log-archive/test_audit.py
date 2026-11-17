"""The audit must detect a missing event and tolerate an exact duplicate."""

import tempfile
import unittest
from pathlib import Path

from audit import compare, load

HERE = Path(__file__).resolve().parent


class ArchiveAuditTest(unittest.TestCase):
    def test_duplicate_is_reported_and_gap_fails(self):
        self.assertEqual(compare(HERE / "source.jsonl", HERE / "archive.jsonl"), ([], 1))
        errors, duplicates = compare(HERE / "source.jsonl", HERE / "archive-defect.jsonl")
        self.assertEqual(duplicates, 0)
        self.assertIn("missing archived event evt-204", errors)

    def test_conflicting_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.jsonl"
            line = (HERE / "archive.jsonl").read_text().splitlines()[0]
            path.write_text(line + "\n" + line.replace("confirmed", "database-timeout") + "\n")
            with self.assertRaisesRegex(ValueError, "conflicting copies"):
                load(path)


if __name__ == "__main__":
    unittest.main()
