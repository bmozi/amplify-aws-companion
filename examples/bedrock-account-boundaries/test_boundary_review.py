import copy
import json
from pathlib import Path
import unittest

from boundary_review import review


CASES = {
    item["id"]: item
    for item in json.loads(Path(__file__).with_name("cases.json").read_text())["cases"]
}


class BoundaryReviewTests(unittest.TestCase):
    def test_supplied_changed_cases(self):
        expected = {
            "local-us-boundary": [],
            "eu-global-route": ["processing_outside_approved_geography"],
            "shared-role-without-trust-review": ["cross_account_trust_not_reviewed"],
            "logs-placed-in-security-account": ["invocation_log_destination_wrong"],
            "reserve-is-not-spendable": ["credit_reserve_breached"],
            "shared-eu-reviewed-paper-path": [],
        }
        for case_id, holds in expected.items():
            with self.subTest(case=case_id):
                self.assertEqual(review(CASES[case_id])["holds"], holds)

    def test_source_region_rule_rejects_other_destination(self):
        case = copy.deepcopy(CASES["local-us-boundary"])
        case["candidate_processing_regions"].append("us-west-2")
        self.assertIn("processing_outside_source_region", review(case)["holds"])

    def test_content_logging_requires_retention_decision(self):
        case = copy.deepcopy(CASES["local-us-boundary"])
        case["logging"]["content_retention_approved"] = False
        self.assertIn("content_retention_not_approved", review(case)["holds"])

    def test_gross_budget_and_missing_meter_are_distinct(self):
        case = copy.deepcopy(CASES["local-us-boundary"])
        case["cost"]["gross_budget_headroom_usd"] = 7
        case["cost"]["included_meters"].remove("retries")
        result = review(case)
        self.assertIn("gross_budget_exceeded", result["holds"])
        self.assertIn("cost_meters_missing", result["holds"])
        self.assertNotIn("credit_reserve_breached", result["holds"])


if __name__ == "__main__":
    unittest.main()
