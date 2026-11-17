"""Check illustrative fanout arithmetic and refusal of malformed assumptions."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

import lab


PLAN = json.loads(Path(__file__).with_name("plan.json").read_text())


class FanoutTests(unittest.TestCase):
    def test_small_visit_has_multiple_service_meters(self):
        q = lab.trace(PLAN)["quantities"]
        self.assertEqual(q["hosting_transfer_gb"], "0.05")
        self.assertEqual(q["appsync_operations_proxy"], "235.00")
        self.assertEqual(q["appsync_connection_minutes_proxy"], "500")
        self.assertEqual(q["appsync_realtime_updates_proxy"], "25.00")
        self.assertEqual(q["dynamodb_read_units_proxy"], "200")
        self.assertEqual(q["dynamodb_write_units_proxy"], "25.00")
        self.assertEqual(q["s3_upload_requests_proxy"], "5.00")
        self.assertEqual(q["s3_get_requests_proxy"], "5.00")
        self.assertEqual(q["s3_list_requests_proxy"], "105.00")
        self.assertEqual(q["s3_added_storage_gb"], "0.005")
        self.assertEqual(q["lambda_invocations_proxy"], "10.0")
        self.assertEqual(q["lambda_gb_seconds_proxy"], "0.62500")
        self.assertEqual(q["cloudwatch_new_log_gb_proxy"], "0.00002048")
        self.assertEqual(q["cloudwatch_retained_log_gb_month_proxy"], "0.00002048")

    def test_larger_audience_breaks_old_transfer_assumption(self):
        result = lab.trace(PLAN, visits_override="80000")
        self.assertEqual(result["quantities"]["hosting_transfer_gb"], "40")
        self.assertFalse(result["fits_5gb_hosting_transfer_assumption"])

    def test_missing_or_invalid_inputs_stop(self):
        for field, value in (("bytes_per_upload", "NaN"), ("visits", "1.5"),
                             ("lists_per_visit", "-1"), ("saves_per_visit", "0.333"),
                             ("file_downloads_per_visit", "0.333"),
                             ("lambda_memory_gb", "0"),
                             ("lambda_duration_seconds_per_inspection", "0"),
                             ("log_storage_gb_months_per_new_gb", "0")):
            with self.subTest(field=field):
                plan = deepcopy(PLAN)
                plan[field] = value
                with self.assertRaises(ValueError):
                    lab.trace(plan)
        plan = deepcopy(PLAN)
        del plan["log_bytes_per_inspection"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            lab.trace(plan)
        plan = deepcopy(PLAN)
        plan["distinct_signed_in_users"] = "101"
        with self.assertRaisesRegex(ValueError, "exceed visits"):
            lab.trace(plan)


if __name__ == "__main__":
    unittest.main()
