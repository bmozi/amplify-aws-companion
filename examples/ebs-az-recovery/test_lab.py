import unittest

from lab import Case, evaluate


class RecoveryClockTests(unittest.TestCase):
    def test_snapshot_ready_but_business_rpo_fails(self):
        result = evaluate(Case())
        self.assertTrue(result["snapshot_ready_at_failure"])
        self.assertEqual(result["possible_write_loss_window_min"], 4)
        self.assertEqual(result["fictional_recovery_clock_min"], 15)
        self.assertFalse(result["rpo_arithmetic_fits"])
        self.assertTrue(result["rto_arithmetic_fits"])
        self.assertEqual(result["decision"], "HOLD_PROMISE")

    def test_later_snapshot_not_available_at_failure(self):
        result = evaluate(Case(snapshot_captured_min=12,
                               snapshot_available_min=16))
        self.assertFalse(result["snapshot_ready_at_failure"])
        self.assertFalse(result["rpo_arithmetic_fits"])
        self.assertFalse(result["rto_arithmetic_fits"])

    def test_looser_promise_still_needs_a_drill(self):
        result = evaluate(Case(rpo_target_min=5, rto_target_min=20))
        self.assertEqual(result["decision"], "DESIGN_CANDIDATE_NEEDS_DRILL")

    def test_slower_first_read_rejects_even_looser_rto(self):
        result = evaluate(Case(rpo_target_min=5, rto_target_min=20,
                               initialize_min=12))
        self.assertEqual(result["fictional_recovery_clock_min"], 21)
        self.assertFalse(result["rto_arithmetic_fits"])

    def test_impossible_clock_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(Case(snapshot_available_min=9))
        with self.assertRaises(ValueError):
            evaluate(Case(snapshot_captured_min=15))
        with self.assertRaises(ValueError):
            evaluate(Case(detect_min=-1))


if __name__ == "__main__":
    unittest.main()
