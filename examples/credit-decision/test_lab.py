import unittest

from lab import assess, cases, dollars, when


class CreditDecisionTests(unittest.TestCase):
    def test_reviewed_case_is_only_a_candidate(self):
        result = assess(cases()[0])
        self.assertEqual(result["decision"], "candidate_for_separate_live_review")
        self.assertEqual(result["headroom_after_estimate_and_reserve_usd"], "3")
        self.assertEqual(result["reasons"], [])

    def test_independent_blockers_are_not_hidden_by_the_balance(self):
        for case in cases()[1:]:
            with self.subTest(case=case["name"]):
                result = assess(case)
                self.assertEqual(result["decision"], "hold")
                self.assertTrue(result["reasons"])

    def test_two_failures_are_both_reported(self):
        case = cases()[1]
        case["run"]["other_active_runs"] = 1
        result = assess(case)
        self.assertEqual(len(result["reasons"]), 2)
        self.assertIn("Individual credit terms", result["reasons"][0])
        self.assertIn("Another active run", result["reasons"][1])

    def test_invalid_money_and_time_cannot_look_eligible(self):
        for value in ["NaN", "Infinity", "-1", True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                dollars(value)
        with self.assertRaises(ValueError):
            when("2026-10-22T00:00:00")

    def test_expiring_exactly_at_end_is_not_enough(self):
        case = cases()[0]
        case["credit_terms"]["expires_at"] = case["run"]["planned_end"]
        self.assertEqual(assess(case)["decision"], "hold")

    def test_reader_chosen_limit_and_reserve_change_the_decision(self):
        case = cases()[0]
        case["run"]["spending_limit_usd"] = "2"
        self.assertEqual(assess(case)["decision"], "hold")
        case["run"]["spending_limit_usd"] = "10"
        case["run"]["reserve_usd"] = "79"
        self.assertEqual(assess(case)["decision"], "hold")
        case["run"]["reserve_usd"] = "75"
        self.assertEqual(assess(case)["decision"], "candidate_for_separate_live_review")


if __name__ == "__main__":
    unittest.main()
