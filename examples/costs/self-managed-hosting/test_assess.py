import copy
from decimal import Decimal
import json
from pathlib import Path
import unittest

from assess import assess


FIXTURE = json.loads((Path(__file__).parent / "plan.json").read_text())


class PlanTests(unittest.TestCase):
    def test_complete_fictional_plan(self):
        result = assess(FIXTURE)
        self.assertEqual(Decimal(result["base_usd"]), Decimal("1.74"))
        self.assertEqual(Decimal(result["total_usd"]), Decimal("2.24"))
        self.assertEqual(Decimal(result["fictional_remaining_usd"]), Decimal("102.76"))

    def test_default_alarm_cannot_disappear(self):
        plan = copy.deepcopy(FIXTURE)
        plan["meters"] = [row for row in plan["meters"] if row["name"] != "cloudwatch_alarms"]
        with self.assertRaisesRegex(ValueError, "Missing meters"):
            assess(plan)

    def test_selected_waf_cannot_be_marked_not_applicable(self):
        plan = copy.deepcopy(FIXTURE)
        plan["features"]["waf"] = True
        with self.assertRaisesRegex(ValueError, "Selected meter"):
            assess(plan)

    def test_managed_hosting_subtotal_is_not_a_meter(self):
        plan = copy.deepcopy(FIXTURE)
        plan["meters"].append({"name": "amplify_hosting_subtotal", "state": "estimated", "quantity": "1", "rate_usd": "0.75023", "basis": "copied"})
        with self.assertRaisesRegex(ValueError, "copied managed Hosting"):
            assess(plan)

    def test_reserve_and_run_ceiling(self):
        for key, value, message in (("fictional_credit_balance_usd", "101", "reserve"),
                                    ("contingency_usd", "4", "USD 5")):
            with self.subTest(key=key):
                plan = copy.deepcopy(FIXTURE)
                plan[key] = value
                with self.assertRaisesRegex(ValueError, message):
                    assess(plan)

    def test_zero_requires_basis_and_only_fictional_rates(self):
        plan = copy.deepcopy(FIXTURE)
        plan["meters"][0]["basis"] = ""
        with self.assertRaisesRegex(ValueError, "basis"):
            assess(plan)
        plan = copy.deepcopy(FIXTURE)
        plan["price_basis"] = "current_aws_quote"
        with self.assertRaisesRegex(ValueError, "fictional rates"):
            assess(plan)


if __name__ == "__main__":
    unittest.main()
