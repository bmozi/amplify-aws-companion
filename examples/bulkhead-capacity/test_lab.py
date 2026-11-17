import unittest

from lab import Job, run, summary


class BulkheadCapacityTests(unittest.TestCase):
    def test_flood_hurts_shared_workers(self):
        self.assertEqual(summary(separate_workers=False, database_slots=2)["booking_end"], 5)

    def test_separate_workers_protect_booking_with_independent_db_capacity(self):
        self.assertEqual(summary(separate_workers=True, database_slots=2)["booking_end"], 2)

    def test_shared_database_reconnects_failure(self):
        self.assertEqual(summary(separate_workers=True, database_slots=1)["booking_end"], 5)

    def test_changed_arrival_removes_competition(self):
        jobs = (Job("booking", "booking", 0, 1), Job("report", "report", 1, 4))
        self.assertEqual(run(separate_workers=False, database_slots=1, jobs=jobs)["booking"], (0, 1))

    def test_duplicate_job_identity_rejected(self):
        with self.assertRaises(ValueError):
            run(separate_workers=True, database_slots=2,
                jobs=(Job("x", "booking", 0, 1), Job("x", "report", 0, 4)))


if __name__ == "__main__":
    unittest.main()
