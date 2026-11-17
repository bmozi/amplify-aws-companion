import json
from pathlib import Path
import unittest

from lab import review


FIXTURE = Path(__file__).with_name("controls.json")


class ControlMatrixTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text())

    def test_fixture_preserves_missing_stale_and_exception_findings(self):
        issues, total = review(self.data)
        self.assertEqual(total, 30)
        codes = [issue[0] for issue in issues]
        self.assertCountEqual(codes, ["EXCEPTION_REVIEW", "STALE_EVIDENCE", "CONTROL_MISSING"])

    def test_missing_matrix_cell_is_reported(self):
        self.data["observations"].pop()
        issues, _ = review(self.data)
        self.assertIn("MISSING_ROW", [issue[0] for issue in issues])

    def test_duplicate_observation_is_reported(self):
        self.data["observations"].append(self.data["observations"][0].copy())
        issues, _ = review(self.data)
        self.assertIn("DUPLICATE", [issue[0] for issue in issues])

    def test_exception_without_compensating_control_is_rejected(self):
        row = next(r for r in self.data["observations"] if r["status"] == "exception")
        row.pop("compensating_control")
        issues, _ = review(self.data)
        self.assertIn("UNSUPPORTED_EXCEPTION", [issue[0] for issue in issues])

    def test_freshness_limit_is_applied_to_active_observation(self):
        row = next(r for r in self.data["observations"] if r["status"] == "active")
        row["age_hours"] = self.data["max_age_hours"] + 1
        issues, _ = review(self.data)
        self.assertIn("STALE_EVIDENCE", [issue[0] for issue in issues])


if __name__ == "__main__":
    unittest.main()
