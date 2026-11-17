import copy
from decimal import Decimal as D
import json
from pathlib import Path
import unittest

from lab import compare, compare_sizes, prices
from refresh_prices import extract, SELECTIONS

HERE = Path(__file__).resolve().parent


class OhioS3PriceTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads((HERE / "public-prices.json").read_text())
        self.rates = prices(self.snapshot)

    def test_selected_public_snapshot_has_expected_starting_rates(self):
        self.assertEqual(self.snapshot["source"]["sha256"],
                         "52b93329ad3e132d8195b27b027907322a7a142fafef301d55073605826452da")
        self.assertEqual(self.rates["standard_storage"], D(".023"))
        self.assertEqual(self.rates["ia_storage"], D(".0125"))
        self.assertEqual(self.rates["standard_put"], D(".000005"))
        self.assertEqual(self.rates["ia_put"], D(".000010"))
        self.assertEqual(self.rates["ia_early_small_floor"], D(".0125"))

    def test_short_lived_small_and_long_lived_large_reverse_the_choice(self):
        small = compare(objects=10_000, bytes_each=1024, days=10, rates=self.rates)
        self.assertEqual(small["ia_billable_gb"], D("1.220703125"))
        self.assertEqual(small["standard_ia"]["total"], D("0.1152587890625"))
        self.assertLess(small["standard"]["total"], small["standard_ia"]["total"])
        large = compare(objects=100, bytes_each=2**30, days=60, rates=self.rates)
        self.assertEqual(large["standard"]["total"], D("4.6005"))
        self.assertEqual(large["standard_ia"]["total"], D("2.501"))
        self.assertLess(large["standard_ia"]["total"], large["standard"]["total"])

    def test_measured_source_shape_reconciles_and_packing_changes_request_count(self):
        shape = json.loads((HERE / "source-shape.json").read_text())
        self.assertEqual(shape["objects"], 1344)
        self.assertEqual(sum(shape["sizes_bytes"]), shape["unpacked_bytes"])
        separate = compare_sizes(sizes_bytes=shape["sizes_bytes"], days=10, rates=self.rates)
        packed = compare_sizes(sizes_bytes=[shape["archive_bytes"]], days=10, rates=self.rates)
        self.assertEqual(separate["standard"]["puts"], D(".00672"))
        self.assertEqual(packed["standard"]["puts"], D(".000005"))
        self.assertGreater(separate["ia_billable_gb"], packed["ia_billable_gb"])

    def test_invalid_inputs_and_meter_shape_fail(self):
        for patch in ({"objects": True}, {"bytes_each": 0}, {"days": 0}, {"days": 366}):
            with self.assertRaises(ValueError):
                compare(**({"objects": 1, "bytes_each": 1024, "days": 10} | patch), rates=self.rates)
        with self.assertRaises(ValueError):
            compare_sizes(sizes_bytes=[1024, False], days=10, rates=self.rates)
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["rates"]["ia_early_small_floor"]["unit"] = "Requests"
        with self.assertRaisesRegex(ValueError, "wrong rate selection"):
            prices(snapshot)

    def test_offer_selection_rejects_wrong_region_or_usage_type(self):
        products, terms = {}, {}
        for name, (sku, usage, unit) in SELECTIONS.items():
            products[sku] = {"sku": sku, "attributes": {"usagetype": usage, "regionCode": "us-east-2"}}
            terms[sku] = {"term": {"priceDimensions": {"dimension": {
                "beginRange": "0", "unit": unit, "pricePerUnit": {"USD": "0.01"}}}}}
        offer = {"offerCode": "AmazonS3", "products": products, "terms": {"OnDemand": terms}}
        self.assertEqual(len(extract(offer)), len(SELECTIONS))
        bad = copy.deepcopy(offer)
        bad["products"][SELECTIONS["ia_storage"][0]]["attributes"]["regionCode"] = "us-east-1"
        with self.assertRaisesRegex(ValueError, "not Ohio"):
            extract(bad)
        bad = copy.deepcopy(offer)
        bad["products"][SELECTIONS["ia_storage"][0]]["attributes"]["usagetype"] = "wrong"
        with self.assertRaisesRegex(ValueError, "usage type changed"):
            extract(bad)


if __name__ == "__main__":
    unittest.main()
