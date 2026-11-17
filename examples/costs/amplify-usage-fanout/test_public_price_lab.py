import copy
from decimal import Decimal
import json
from pathlib import Path
import unittest

from public_price_lab import price_selected


HERE = Path(__file__).resolve().parent


class PublicPriceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((HERE / "plan.json").read_text())
        cls.scenario = json.loads((HERE / "public-price-scenario.json").read_text())
        cls.snapshot = json.loads((HERE / "public-prices-us-east-2.json").read_text())

    def test_selected_meter_subtotal_never_becomes_a_publisher_estimate(self):
        result = price_selected(self.plan, self.scenario, self.snapshot)
        self.assertEqual(Decimal(result["selected_preallowance_subtotal_usd"]), Decimal("0.384490896087500000"))
        self.assertEqual(result["selected_meters"]["s3_get_request"]["quantity"], "5.00")
        self.assertEqual(result["selected_meters"]["lambda_gb_second_tier_1"]["quantity"], "0.62500")
        self.assertEqual(result["selected_meters"]["cloudwatch_standard_log_storage_gb_month"]["quantity"], "0.00002048")
        self.assertEqual(result["status"], "incomplete_selected_meter_subtotal_only")
        self.assertTrue(result["not_a_publisher_estimate"])
        self.assertIn("Actual DynamoDB billing mode", " ".join(result["missing_for_whole_run"]))
        self.assertNotIn("estimated_run_usd", result)

    def test_changed_audience_breaks_five_gb_assumption_without_completing_estimate(self):
        plan = dict(self.plan, visits="80000")
        result = price_selected(plan, self.scenario, self.snapshot)
        self.assertEqual(result["selected_meters"]["hosting_transfer_gb"]["quantity"], "40")
        self.assertFalse(result["fits_5gb_hosting_transfer_assumption_only"])
        self.assertTrue(result["not_a_publisher_estimate"])

    def test_one_audience_can_break_cost_limit_before_omitted_meters(self):
        plan = json.loads((HERE / "publisher-audience-plan.json").read_text())
        result = price_selected(plan, self.scenario, self.snapshot)
        self.assertEqual(result["selected_meters"]["hosting_transfer_gb"]["quantity"], "5")
        self.assertEqual(result["selected_meters"]["cognito_essentials_mau_before_free_tier"]["quantity"], "2500")
        self.assertGreater(Decimal(result["selected_preallowance_subtotal_usd"]), Decimal("5"))
        self.assertTrue(result["not_a_publisher_estimate"])

    def test_missing_meter_forged_source_and_nonfinite_price_fail(self):
        for edit in (
            lambda x: x["rates"].pop("appsync_graphql_operation"),
            lambda x: x["offers"]["AWSAmplify"].update(url="https://example.invalid/index.json"),
            lambda x: x["rates"]["cognito_essentials_mau_before_free_tier"].update(usd_per_unit="NaN"),
        ):
            snapshot = copy.deepcopy(self.snapshot)
            edit(snapshot)
            with self.subTest(snapshot=snapshot.get("rates", {}).keys()), self.assertRaises(ValueError):
                price_selected(self.plan, self.scenario, snapshot)

    def test_scenario_cannot_claim_reviewed_run(self):
        with self.assertRaises(ValueError):
            price_selected(self.plan, dict(self.scenario, status="reviewed"), self.snapshot)


if __name__ == "__main__":
    unittest.main()
