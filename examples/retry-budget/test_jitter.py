import unittest
from jitter import schedule, compare


class JitterReasoningTests(unittest.TestCase):
    def test_fixed_clients_remain_synchronized(self):
        result = compare()['fixed']
        self.assertEqual(result['retry_starts_per_one_second_bucket'], {3: 20, 8: 20})
        self.assertEqual(result['total_calls'], 60)

    def test_shorter_waits_can_admit_more_calls_without_any_success(self):
        self.assertEqual(schedule([0, 0, 0]), [0, 1, 2, 3])
        self.assertEqual(len(schedule([1, 1, 1])), 3)
        self.assertEqual(compare()['full_jitter']['completed_customer_operations'], 0)

    def test_jitter_does_not_guarantee_separation(self):
        first = schedule([.5, .5, .5])
        second = schedule([.5, .5, .5])
        self.assertEqual(first, second)

    def test_deadline_includes_duration_and_exact_finish_is_allowed(self):
        self.assertEqual(schedule([0, 0, 0], deadline=2), [0, 1])
        self.assertEqual(schedule([0, 0, 0], deadline=.5), [])
        for seed in range(20):
            # Explicit draws check boundary cases without flaky random assertions.
            draws = [seed / 20] * 3
            self.assertTrue(all(t + 1 <= 12 for t in schedule(draws)))

    def test_bad_timing_inputs_are_rejected(self):
        for draws in ([0], [0, -1, 0], [0, float('nan'), 0]):
            with self.assertRaises(ValueError):
                schedule(draws)
        with self.assertRaises(ValueError):
            schedule([0, 0, 0], call_seconds=0)


if __name__ == '__main__':
    unittest.main()
