import unittest

from pickup_window import two_stage


class PickupWindowTests(unittest.TestCase):
    def test_fast_dispatch_does_not_make_every_pickup_ready(self):
        result = two_stage()
        branches = result["branches"]
        self.assertEqual(sum(row["jobs"] for row in branches.values()), 460)
        self.assertEqual(sum(row["dispatched_within_30_minutes"] for row in branches.values()), 460)
        self.assertLess(sum(row["ready_within_30_minutes"] for row in branches.values()), 460)

    def test_ready_deadline_cannot_be_met_more_often_than_dispatch_deadline(self):
        result = two_stage(pickup_seconds=1)
        for row in result["branches"].values():
            self.assertLessEqual(row["ready_within_30_minutes"],
                                 row["dispatched_within_30_minutes"])

    def test_second_stage_policy_changes_who_is_timely(self):
        fifo = two_stage(pickup_policy="fifo")
        fair = two_stage(pickup_policy="round-robin")
        self.assertGreater(fair["branches"]["B"]["ready_within_30_minutes"],
                           fifo["branches"]["B"]["ready_within_30_minutes"])
        self.assertLess(fair["branches"]["A"]["ready_within_30_minutes"],
                        fifo["branches"]["A"]["ready_within_30_minutes"])

    def test_invalid_duration_or_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            two_stage(pickup_seconds=0)
        with self.assertRaises(ValueError):
            two_stage(dispatch_policy="unknown")


if __name__ == "__main__":
    unittest.main()
