"""Check the lesson's changed-condition claims against the FIFO fixture."""

import unittest
from lab import ARRIVALS, trace


class ArrivalShapeTests(unittest.TestCase):
    def test_same_total_changes_lateness(self):
        even = trace(ARRIVALS["even"], 10, 10)
        burst = trace(ARRIVALS["burst"], 10, 10)
        self.assertEqual(even["accepted"], burst["accepted"])
        self.assertEqual((even["peak_unfinished"], even["late_over_one_bucket"]), (0, 0))
        self.assertEqual((burst["peak_unfinished"], burst["late_over_one_bucket"]), (16, 6))

    def test_downstream_limit_and_changed_arrival_shape(self):
        baseline = trace(ARRIVALS["burst"], 10, 10)
        self.assertEqual(trace(ARRIVALS["burst"], 12, 10), baseline)
        reviewed = trace(ARRIVALS["burst"], 12, 12)
        self.assertEqual((reviewed["peak_unfinished"], reviewed["late_over_one_bucket"]), (12, 0))
        moved = trace((6, 0, 12, 18, 0, 0), 10, 10)
        self.assertEqual(moved["accepted"], baseline["accepted"])
        self.assertEqual([row["unfinished"] for row in moved["rows"]], [0, 0, 2, 10, 0, 0])
        self.assertEqual(moved["late_over_one_bucket"], 0)


if __name__ == "__main__":
    unittest.main()
