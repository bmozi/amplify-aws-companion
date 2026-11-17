import unittest

from lab import Policy, SHARED_BUDGET, SINGLE_LAYER, STACKED, fictional_cost, simulate


class RetryDecisionTests(unittest.TestCase):
    def test_two_layers_multiply_failed_work_and_miss_the_customer_deadline(self):
        uncontrolled = simulate(STACKED)
        bounded = simulate(SINGLE_LAYER)
        self.assertEqual(uncontrolled, {
            "calls": 9, "elapsed_seconds": 30, "outcome": "attempts_exhausted"
        })
        self.assertEqual(bounded, {
            "calls": 3, "elapsed_seconds": 9, "outcome": "attempts_exhausted"
        })
        self.assertEqual(fictional_cost(uncontrolled["calls"], 100), "0.900")
        self.assertEqual(fictional_cost(bounded["calls"], 100), "0.300")

    def test_shared_budget_blocks_an_inner_retry_even_with_outer_attempts_left(self):
        result = simulate(SHARED_BUDGET)
        self.assertEqual(result["calls"], 3)
        self.assertEqual(result["elapsed_seconds"], 9)
        self.assertEqual(result["outcome"], "call_budget_exhausted")

    def test_some_retries_save_a_transient_request_but_not_a_permanent_denial(self):
        self.assertEqual(simulate(SINGLE_LAYER, succeeds_on=3)["outcome"], "completed")
        self.assertEqual(simulate(SINGLE_LAYER, failure="permanent"), {
            "calls": 1, "elapsed_seconds": 2, "outcome": "permanent_error"
        })

    def test_deadline_and_price_are_not_assumed_to_be_infinite(self):
        self.assertEqual(simulate(Policy(1, 3, 3, 8))["outcome"], "deadline_exhausted")
        self.assertEqual(simulate(Policy(1, 3, 3, 8))["calls"], 2)
        self.assertEqual(simulate(Policy(1, 3, 3, 1))["calls"], 0)
        with self.assertRaises(ValueError):
            fictional_cost(3, 100, "NaN")

    def test_retry_wait_is_skipped_when_next_call_cannot_finish(self):
        self.assertEqual(simulate(Policy(1, 3, 3, 8)), {
            "calls": 2, "elapsed_seconds": 5, "outcome": "deadline_exhausted"
        })
        self.assertEqual(simulate(Policy(3, 1, None, 4)), {
            "calls": 1, "elapsed_seconds": 2, "outcome": "deadline_exhausted"
        })
        self.assertEqual(simulate(Policy(1, 2, None, 5), succeeds_on=2), {
            "calls": 2, "elapsed_seconds": 5, "outcome": "completed"
        })


if __name__ == "__main__":
    unittest.main()
