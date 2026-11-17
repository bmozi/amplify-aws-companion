import unittest

from lab import Case, evaluate


class EbsEconomicsTests(unittest.TestCase):
    def test_base_case_separates_capacity_and_performance(self):
        result = evaluate(Case())
        self.assertEqual(result["gp2"]["provisioned_gib_for_sustained_iops"], 2000)
        self.assertEqual(result["gp2"]["fictional_monthly_usd"], "200.00")
        self.assertEqual(result["gp3"]["fictional_monthly_usd"], "67.500")
        self.assertEqual(result["io2"]["fictional_monthly_usd_first_tier_only"], "465.000")

    def test_instance_ceiling_holds_both_general_purpose_candidates(self):
        result = evaluate(Case(instance_iops_ceiling=4000))
        self.assertTrue(result["instance_holds"])
        self.assertFalse(result["gp2"]["shape_feasible"])
        self.assertFalse(result["gp3"]["shape_feasible"])

    def test_throughput_change_rejects_gp2_but_not_gp3(self):
        result = evaluate(Case(sequential_mib_s=300))
        self.assertFalse(result["gp2"]["shape_feasible"])
        self.assertTrue(result["gp3"]["shape_feasible"])
        self.assertEqual(result["gp3"]["fictional_monthly_usd"], "73.500")

    def test_invalid_or_unpriced_input_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(Case(sustained_iops=0))
        with self.assertRaises(ValueError):
            evaluate(Case(sustained_iops=32001))


if __name__ == "__main__":
    unittest.main()
