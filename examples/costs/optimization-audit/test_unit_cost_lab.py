import csv
from decimal import Decimal
import tempfile
from pathlib import Path
import unittest

from lab import HERE, load_adjustments, load_lines, reconcile
from unit_cost_lab import direct_tagged_proxy, load_outcomes


class UnitCostBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.totals = reconcile(load_lines(HERE / "line-items.csv"),
                                load_adjustments(HERE / "adjustments.csv"))
        self.counts = load_outcomes(HERE / "outcome-counts.csv")

    def test_partial_numerator_and_fewer_qualifying_results(self):
        result = direct_tagged_proxy(self.totals, self.counts)
        self.assertEqual(result["baseline"]["direct_tagged_usd_per_qualifying_repair_proxy"], "0.078")
        self.assertEqual(result["current"]["direct_tagged_usd_per_qualifying_repair_proxy"], "0.0975")
        self.assertEqual(result["current"]["unallocated_precredit_usd"], "27.00")
        self.assertNotIn("full_repair_unit_cost", result["current"])

    def test_zero_outputs_is_undefined_while_charges_remain(self):
        counts = dict(self.counts, current=0)
        result = direct_tagged_proxy(self.totals, counts)["current"]
        self.assertIsNone(result["direct_tagged_usd_per_qualifying_repair_proxy"])
        self.assertEqual(result["account_precredit_usd_context_only"], "117.00")

    def test_wrong_population_and_fractional_counts_fail(self):
        for counts in (dict(self.counts, current=-1), dict(self.counts, current=Decimal("1.5")),
                       {"current": 800}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                direct_tagged_proxy(self.totals, counts)

    def test_duplicate_period_or_false_provenance_fails(self):
        with (HERE / "outcome-counts.csv").open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "outcomes.csv"
            for candidate in (rows + [dict(rows[1])],
                              [rows[0], dict(rows[1], provenance="measured_aws")]):
                with path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(candidate)
                with self.assertRaises(ValueError):
                    load_outcomes(path)


if __name__ == "__main__":
    unittest.main()
