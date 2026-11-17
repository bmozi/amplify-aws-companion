import copy
import json
from pathlib import Path
import unittest

from route_review import review


CASES = {case["id"]: case for case in json.loads(Path(__file__).with_name("cases.json").read_text())["cases"]}


class RouteReviewTests(unittest.TestCase):
    def test_six_changed_routes(self):
        expected = {
            "direct-reviewed-route": [],
            "bus-policy-only": ["sender_role_not_reviewed"],
            "broad-receiver-rule": ["receiver_rule_scope_not_reviewed"],
            "third-hop-and-wrong-replay": ["unsupported_third_bus_hop", "archive_replay_wrong_bus"],
            "lost-failure-and-duplicate-effect": ["receiver_target_permission_missing", "forwarding_failure_destination_missing", "receiver_failure_destination_missing", "replay_effect_deduplication_missing"],
            "reserve-is-not-routing-permission": ["credit_reserve_breached"],
        }
        for name, holds in expected.items():
            with self.subTest(case=name):
                self.assertEqual(review(CASES[name])["holds"], holds)

    def test_destination_region_and_bus_policy_are_separate(self):
        case = copy.deepcopy(CASES["direct-reviewed-route"])
        case["destination"]["region_supported"] = False
        case["receiving_bus"]["allowed_sender_accounts"] = []
        result = review(case)
        self.assertIn("destination_region_not_reviewed", result["holds"])
        self.assertIn("receiver_bus_does_not_admit_sender", result["holds"])

    def test_cost_meters_and_gross_headroom_are_separate(self):
        case = copy.deepcopy(CASES["direct-reviewed-route"])
        case["cost"]["included_meters"].remove("archive")
        case["cost"]["gross_headroom_usd"] = 7
        result = review(case)
        self.assertIn("route_cost_meters_missing", result["holds"])
        self.assertIn("gross_budget_exceeded", result["holds"])
        self.assertNotIn("credit_reserve_breached", result["holds"])


if __name__ == "__main__":
    unittest.main()
