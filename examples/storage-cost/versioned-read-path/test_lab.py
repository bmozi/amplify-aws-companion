from decimal import Decimal as D
import json
import unittest

from lab import COMMON, REMOVED_OLD_VERSION, RETAINED_VERSIONS, estimate
from priced_lab import SNAPSHOT, price_scenario
from refresh_prices import extract


class VersionedReadPathTests(unittest.TestCase):
    def setUp(self):
        self.original = {"name": "original", "bytes": 4 * 2**20,
                         "created_day": 0, "removed_day": 30}
        self.replacement = {"name": "replacement", "bytes": 6 * 2**20,
                            "created_day": 10, "removed_day": 30}
        self.common = {"horizon_day": 30, "puts": 2, "gets": 40,
                       "transfer_out_bytes": 40 * 6 * 2**20}

    def test_old_version_keeps_accruing_after_delete_marker(self):
        retained = estimate(versions=[self.original, self.replacement], **self.common)
        expired = estimate(versions=[self.original | {"removed_day": 20}, self.replacement], **self.common)
        self.assertEqual(retained["version_byte_days"], 240 * 2**20)
        self.assertEqual(expired["version_byte_days"], 200 * 2**20)
        self.assertGreater(retained["modeled_subtotal_cu"], expired["modeled_subtotal_cu"])
        self.assertEqual(retained["components_cu"]["get_requests"], D("0.00040"))
        self.assertFalse(retained["approved_to_deploy"])

    def test_kms_counts_are_inputs_not_guessed_from_gets(self):
        missing = estimate(versions=[self.original], **self.common)
        counted = estimate(versions=[self.original], kms_requests=17,
                           kms_key_months="1", **self.common)
        self.assertNotIn("kms_requests", missing["components_cu"])
        self.assertEqual(counted["components_cu"]["kms_requests"], D("0.00034"))
        self.assertEqual(counted["components_cu"]["kms_key_time"], D("0.5"))
        self.assertFalse(counted["approved_to_deploy"])

    def test_invalid_lifetimes_and_counts_fail(self):
        for changed in ({"removed_day": 0}, {"created_day": 30}, {"bytes": 0}):
            with self.assertRaises(ValueError):
                estimate(versions=[self.original | changed], **self.common)
        with self.assertRaises(ValueError):
            estimate(versions=[self.original], **(self.common | {"gets": True}))

    def test_dated_usd_comparison_separates_transfer_from_retention(self):
        snapshot = json.loads(SNAPSHOT.read_text())
        retained = price_scenario(RETAINED_VERSIONS, COMMON, snapshot)
        removed = price_scenario(REMOVED_OLD_VERSION, COMMON, snapshot)
        self.assertEqual(retained["components_usd"]["internet_out"], D("0.021093750000000"))
        self.assertEqual(retained["components_usd"]["standard_get"], D("0.0000160000"))
        self.assertEqual(retained["components_usd"]["standard_put"], D("0.0000100000"))
        self.assertEqual(retained["components_usd"]["internet_out"],
                         removed["components_usd"]["internet_out"])
        self.assertEqual((retained["gross_selected_subtotal_usd"]
                          - removed["gross_selected_subtotal_usd"]).quantize(D("0.000000000000001")),
                         (D(40) / D(1024) / D(30) * D("0.0230000000")).quantize(D("0.000000000000001")))
        self.assertFalse(retained["approved_to_deploy"])
        self.assertTrue(any("Free plan" in item for item in retained["unpriced_or_unverified"]))

    def test_usd_worksheet_rejects_bad_rate_or_unpriced_tier(self):
        snapshot = json.loads(SNAPSHOT.read_text())
        changed = json.loads(json.dumps(snapshot))
        changed["rates"]["standard_get"]["unit"] = "GB"
        with self.assertRaises(ValueError):
            price_scenario(RETAINED_VERSIONS, COMMON, changed)
        changed = json.loads(json.dumps(snapshot))
        changed["rates"]["internet_out"]["end_range"] = "0.1"
        with self.assertRaises(ValueError):
            price_scenario(RETAINED_VERSIONS, COMMON, changed)

    def test_offer_selection_rejects_changed_sku_usage(self):
        with self.assertRaises(ValueError):
            extract({"s3": {"offerCode": "AmazonS3", "products": {}, "terms": {}},
                     "transfer": {"offerCode": "AWSDataTransfer", "products": {}, "terms": {}}})


if __name__ == "__main__":
    unittest.main()
