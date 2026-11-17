import copy
import json
import unittest
from decimal import Decimal

from lab import HERE, review


class InferenceRoutingTests(unittest.TestCase):
    def setUp(self):
        self.scenario = json.loads((HERE / "scenario.json").read_text())

    def test_cheaper_route_is_rejected_when_destination_is_unapproved(self):
        results = {result["name"]: result for result in review(self.scenario)}
        self.assertTrue(results["geographic-profile"]["eligible_by_location"])
        self.assertFalse(results["global-profile"]["eligible_by_location"])
        self.assertEqual(results["global-profile"]["unapproved_destinations"], ["eu-west-1"])
        self.assertLess(results["global-profile"]["token_subtotal_usd"], results["geographic-profile"]["token_subtotal_usd"])

    def test_cache_miss_changes_bill_without_promising_cache_hit(self):
        original = review(self.scenario)[0]["token_subtotal_usd"]
        changed = copy.deepcopy(self.scenario)
        changed["usage_tokens"]["standard_input"] = "1000000"
        changed["usage_tokens"]["cache_read_input"] = "0"
        changed["usage_tokens"]["cache_write_input"] = "0"
        self.assertGreater(review(changed)[0]["token_subtotal_usd"], original)

    def test_global_only_becomes_location_eligible_after_rule_changes(self):
        changed = copy.deepcopy(self.scenario)
        changed["allowed_processing_regions"].append("eu-west-1")
        self.assertTrue(review(changed)[2]["eligible_by_location"])

    def test_unlabeled_or_invalid_prices_are_rejected(self):
        changed = copy.deepcopy(self.scenario)
        changed["fictional"] = False
        with self.assertRaises(ValueError):
            review(changed)
        changed = copy.deepcopy(self.scenario)
        changed["candidates"][0]["fictional_usd_per_million_tokens"]["output"] = "NaN"
        with self.assertRaises(ValueError):
            review(changed)


if __name__ == "__main__":
    unittest.main()
