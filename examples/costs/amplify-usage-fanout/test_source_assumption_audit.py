"""Changed-source cases for the fictional cost-input audit."""

from copy import deepcopy
from decimal import Decimal
import json
import unittest

from source_assumption_audit import PLAN, FUNCTION, BROWSER, audit


class SourceAssumptionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text())
        cls.function_source = FUNCTION.read_text()
        cls.browser_source = BROWSER.read_text()

    def test_current_source_exposes_two_distinct_assumptions(self):
        result = audit(self.plan, self.function_source, self.browser_source)
        self.assertEqual(result["source_settings"]["function_memory_mb"], 128)
        self.assertEqual(result["source_settings"]["browser_upload_limit_bytes"], 5242880)
        self.assertEqual(Decimal(result["changed_cases"]["lambda_gb_seconds_with_source_memory_and_assumed_duration"]), Decimal("0.3125"))
        self.assertEqual(Decimal(result["changed_cases"]["s3_added_gb_if_every_planned_upload_reaches_browser_cap"]), Decimal("0.0262144"))
        self.assertFalse(result["can_approve_publisher_estimate"])

    def test_changed_function_memory_changes_duration_sensitivity(self):
        changed = self.function_source.replace("memoryMB: 128", "memoryMB: 512")
        self.assertNotEqual(changed, self.function_source)
        result = audit(self.plan, changed, self.browser_source)
        self.assertEqual(Decimal(result["changed_cases"]["lambda_gb_seconds_with_source_memory_and_assumed_duration"]), Decimal("1.25"))

    def test_changed_upload_limit_changes_storage_stress_case(self):
        changed = self.browser_source.replace("file.size>5*1024*1024", "file.size>10*1024*1024")
        self.assertNotEqual(changed, self.browser_source)
        result = audit(self.plan, self.function_source, changed)
        self.assertEqual(Decimal(result["changed_cases"]["s3_added_gb_if_every_planned_upload_reaches_browser_cap"]), Decimal("0.0524288"))

    def test_unrecognized_source_setting_requires_manual_review(self):
        changed = self.function_source.replace("memoryMB: 128", "memoryMB: 128 + extra")
        with self.assertRaisesRegex(ValueError, "Cannot identify one function memory"):
            audit(self.plan, changed, self.browser_source)

    def test_plan_memory_match_does_not_approve_live_cost(self):
        changed = deepcopy(self.plan)
        changed["lambda_memory_gb"] = "0.125"
        result = audit(changed, self.function_source, self.browser_source)
        self.assertFalse(result["plan_memory_differs_from_source"])
        self.assertFalse(result["can_approve_publisher_estimate"])


if __name__ == "__main__":
    unittest.main()
