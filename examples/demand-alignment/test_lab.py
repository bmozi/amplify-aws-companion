import unittest
from lab import simulate


class DemandEnvelopeTests(unittest.TestCase):
    def test_same_correct_work_exposes_provisioned_idle_time(self):
        burst = (90,) + (0,) * 7
        always = simulate(burst, (4,) * 8)
        scaled = simulate(burst, (2,) * 4 + (0,) * 4)
        self.assertEqual((always.timely, scaled.timely), (90, 90))
        self.assertEqual((always.worker_minutes, scaled.worker_minutes), (32, 8))
        self.assertEqual((always.backlog_at_deadline, scaled.backlog_at_deadline), (0, 0))

    def test_smaller_number_is_not_a_valid_deadline_comparison(self):
        result = simulate((90,) + (0,) * 7, (1,) * 6 + (0,) * 2)
        self.assertEqual((result.timely, result.late, result.worker_minutes), (60, 30, 6))
        self.assertEqual(result.backlog_at_deadline, 30)

    def test_outage_removes_deadline_margin_even_if_work_finishes_later(self):
        result = simulate((90,) + (0,) * 7, (2, 1, 1, 1, 1, 1, 0, 0))
        self.assertEqual((result.timely, result.late, result.unfinished), (75, 15, 0))

    def test_changed_burst_consumes_margin(self):
        burst = (120,) + (0,) * 7
        nominal = simulate(burst, (2,) * 4 + (0,) * 4)
        interrupted = simulate(burst, (2, 2, 1, 2, 0, 0, 0, 0))
        self.assertEqual(nominal.timely, 120)
        self.assertEqual((interrupted.timely, interrupted.unfinished), (105, 15))

    def test_refuses_incomplete_or_post_deadline_input(self):
        with self.assertRaises(ValueError):
            simulate((1, 0, 0), (1, 1), deadline=2)
        with self.assertRaises(ValueError):
            simulate((1, 0, 1), (1, 1, 1), deadline=2)


if __name__ == "__main__":
    unittest.main()
