"""Check that missing synthetic observations cannot become measured bytes."""
import csv
import tempfile
import unittest
from pathlib import Path

from lab import summarize


class MissingFlowEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "flows.csv"

    def write_rows(self, rows):
        with self.path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=("source_group", "action", "bytes", "status", "window"))
            writer.writeheader()
            writer.writerows(rows)

    def test_skipped_interval_is_not_a_zero_or_measured_byte_row(self):
        self.write_rows([
            dict(source_group="app-a", action="ACCEPT", bytes="13", status="OK", window="w1"),
            dict(source_group="app-a", action="-", bytes="", status="SKIPDATA", window="w1"),
        ])
        totals, statuses = summarize(self.path)
        self.assertEqual(totals[("app-a", "ACCEPT")], 13)
        self.assertEqual(sum(totals.values()), 13)
        self.assertEqual(statuses["SKIPDATA"], 1)

    def test_fake_numeric_bytes_on_skipped_marker_are_rejected(self):
        self.write_rows([
            dict(source_group="app-a", action="ACCEPT", bytes="8000000000", status="SKIPDATA", window="w1"),
        ])
        with self.assertRaisesRegex(ValueError, "SKIPDATA cannot supply measured"):
            summarize(self.path)


if __name__ == "__main__":
    unittest.main()
