import copy
import json
import unittest

from retention_cost import FIXTURE, evaluate


class RetentionCostTests(unittest.TestCase):
    def setUp(self):
        self.study = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_retained_overlap_has_cost_even_before_other_categories(self):
        result = evaluate(self.study)
        self.assertEqual(result["old_retained_storage_usd"], "0.42")
        self.assertEqual(result["combined_storage_usd"], "0.672")
        self.assertEqual(result["decision"], "HOLD_FULL_COST_AND_CLEANUP")
        self.assertFalse(result["live_aws_price_or_bill_observed"])

    def test_low_subtotal_cannot_clear_unpriced_or_unverified_work(self):
        study = copy.deepcopy(self.study)
        study["days_both_buckets_exist"] = 1
        result = evaluate(study)
        self.assertLess(float(result["combined_storage_usd"]), 0.1)
        self.assertEqual(result["decision"], "HOLD_FULL_COST_AND_CLEANUP")
        self.assertIn("old_bucket_deletion_verified", result["missing_evidence"])

    def test_invalid_or_unmarked_fixture_is_rejected(self):
        study = copy.deepcopy(self.study)
        study["fictional_usd_per_gib_month"] = "NaN"
        with self.assertRaises(ValueError):
            evaluate(study)
        study = copy.deepcopy(self.study)
        study["study_only"] = False
        with self.assertRaises(ValueError):
            evaluate(study)


if __name__ == "__main__":
    unittest.main()
