import unittest

from queue_window import comparison, dispatch, make_arrivals


class QueueWindowTests(unittest.TestCase):
    def test_same_jobs_and_worker_seconds_under_both_rules(self):
        jobs = make_arrivals("even")
        self.assertEqual(len(jobs), 460)
        self.assertEqual(len({job.job_id for job in jobs}), 460)
        for policy in ("fifo", "round-robin"):
            results = dispatch(jobs, policy, 30)
            self.assertEqual({result.job_id for result in results},
                             {job.job_id for job in jobs})
            self.assertTrue(all(result.finished - result.started == 30
                                and result.started >= result.arrived
                                for result in results))

    def test_quiet_branches_gain_time_but_burst_branch_does_not(self):
        result = comparison()
        for branch in ("B", "C", "D"):
            self.assertEqual(result["fifo"]["branches"][branch]["within_30_minutes"], 4)
            self.assertEqual(result["round_robin"]["branches"][branch]["within_30_minutes"], 20)
        self.assertLess(result["round_robin"]["branches"]["A"]["within_30_minutes"],
                        result["fifo"]["branches"]["A"]["within_30_minutes"])
        self.assertLess(sum(x["within_30_minutes"] for x in result["round_robin"]["branches"].values()), 460)

    def test_same_hour_count_different_peak_changes_results(self):
        even = comparison("even")
        front = comparison("front-loaded")
        self.assertEqual(even["fifo"]["total"], front["fifo"]["total"])
        self.assertLess(front["fifo"]["branches"]["B"]["within_30_minutes"],
                        even["fifo"]["branches"]["B"]["within_30_minutes"])
        self.assertGreater(front["fifo"]["branches"]["A"]["p95_minutes"],
                           even["fifo"]["branches"]["A"]["p95_minutes"])

    def test_faster_fictional_worker_changes_capacity_not_identity(self):
        fast = comparison("even", 5)
        self.assertEqual(sum(v["within_30_minutes"]
                             for v in fast["fifo"]["branches"].values()), 460)
        self.assertEqual(sum(v["within_30_minutes"]
                             for v in fast["round_robin"]["branches"].values()), 460)

    def test_invalid_input_is_not_silently_simulated(self):
        jobs = make_arrivals("even")
        with self.assertRaises(ValueError):
            dispatch(jobs, "fifo", 0)
        with self.assertRaises(ValueError):
            dispatch(jobs + [jobs[0]], "fifo", 30)
        with self.assertRaises(ValueError):
            make_arrivals("unknown")


if __name__ == "__main__":
    unittest.main()
