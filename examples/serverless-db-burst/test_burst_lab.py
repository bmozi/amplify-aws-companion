import unittest

from burst_lab import direct_burst, queued_work


class BurstLabTests(unittest.TestCase):
    def test_six_direct_handlers_compete_for_two_slots(self):
        result = direct_burst()
        self.assertEqual((result["saved"], result["database_busy"]), (2, 4))
        self.assertEqual(len(result["results"]), 6)

    def test_an_extra_slot_changes_the_direct_result(self):
        result = direct_burst(database_slots=3)
        self.assertEqual((result["saved"], result["database_busy"]), (3, 3))

    def test_queued_workers_complete_every_unique_job_with_two_slots(self):
        result = queued_work()
        self.assertEqual((result["completed"], result["unique_completed"], result["remaining"]), (6, 6, 0))
        self.assertEqual(result["peak_database_slots_used"], 2)

    def test_more_consumers_do_not_expand_one_database_slot(self):
        result = queued_work(consumers=3, database_slots=1)
        self.assertEqual((result["completed"], result["unique_completed"], result["remaining"]), (6, 6, 0))
        self.assertEqual(result["peak_database_slots_used"], 1)

    def test_invalid_capacity_is_rejected(self):
        with self.assertRaises(ValueError):
            direct_burst(database_slots=0)
        with self.assertRaises(ValueError):
            queued_work(consumers=0)


if __name__ == "__main__":
    unittest.main()
