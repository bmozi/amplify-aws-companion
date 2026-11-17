import json
import unittest
from pathlib import Path

from cutover import review


CASE = json.loads(Path(__file__).with_name("cutover-case.json").read_text())


class CutoverReviewTest(unittest.TestCase):
    def test_one_active_miss_keeps_scan_despite_later_clean_window(self):
        result = review(CASE)
        self.assertEqual(result["recommendation"], "keep_scan")
        self.assertIn("observed_index_miss_needs_investigation", result["reasons"])
        self.assertEqual(result["windows"][1]["stale_candidates_to_base_check"], ["R2"])

    def test_clean_pilot_still_requires_scan_fallback(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][1]["index_visible"] = ["R1", "R3"]
        result = review(case)
        self.assertEqual(result["recommendation"], "consider_bounded_pilot_with_scan_fallback")
        self.assertIn("periodic_complete_reconciliation", result["required_even_for_pilot"])

    def test_active_state_does_not_override_key_violation(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][1]["index_visible"] = ["R1", "R3"]
        case["key_violations"] = ["R4"]
        self.assertIn("unresolved_index_key_violations", review(case)["reasons"])

    def test_incomplete_scan_cannot_claim_no_misses(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][1]["index_visible"] = ["R1", "R3"]
        case["windows"][2]["scan_complete"] = False
        self.assertIn("incomplete_base_reconciliation", review(case)["reasons"])

    def test_cost_and_owner_are_independent_gates(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][1]["index_visible"] = ["R1", "R3"]
        case["cost_reviewed"] = False
        case["operator_assigned"] = False
        self.assertIn("whole_run_cost_not_reviewed", review(case)["reasons"])
        self.assertIn("no_reconciliation_owner", review(case)["reasons"])

    def test_bad_evidence_is_rejected(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][0]["base_due"] = ["R1", "R1"]
        with self.assertRaises(ValueError):
            review(case)

    def test_status_regression_is_rejected(self):
        case = json.loads(json.dumps(CASE))
        case["windows"][2]["status"] = "CREATING"
        with self.assertRaises(ValueError):
            review(case)


if __name__ == "__main__":
    unittest.main()
