import unittest
from fractions import Fraction

from lab import candidate_total, ebs_ceiling_screen, request_total


class BoundaryMathTests(unittest.TestCase):
    def test_a_candidate_must_close_the_customer_gap(self):
        stages = {"app_cpu": 110, "file_wait": 260, "database_wait": 420, "other": 90}
        self.assertEqual(request_total(stages), 880)
        self.assertEqual(candidate_total(stages, "file_wait", 130), 750)
        self.assertEqual(candidate_total(stages, "database_wait", 300), 580)
        self.assertGreater(candidate_total(stages, "file_wait", 130), 600)
        self.assertLessEqual(candidate_total(stages, "database_wait", 300), 600)

    def test_volume_and_instance_limits_can_bind_differently(self):
        volume = ebs_ceiling_screen(6000, 4, 3000, 125, 7000, 100)
        self.assertEqual(volume["demand_mib_per_second"], Fraction(375, 16))
        self.assertTrue(volume["volume_iops_exceeded"])
        self.assertFalse(volume["instance_iops_exceeded"])
        instance = ebs_ceiling_screen(3500, 4, 5000, 125, 3000, 100)
        self.assertFalse(instance["volume_iops_exceeded"])
        self.assertTrue(instance["instance_iops_exceeded"])

    def test_large_io_changes_the_binding_dimension(self):
        result = ebs_ceiling_screen(4000, 256, 8000, 750, 8000, 900)
        self.assertEqual(result["demand_mib_per_second"], 1000)
        self.assertFalse(result["volume_iops_exceeded"])
        self.assertFalse(result["instance_iops_exceeded"])
        self.assertTrue(result["volume_throughput_exceeded"])
        self.assertTrue(result["instance_throughput_exceeded"])

    def test_invalid_counterexamples_are_rejected(self):
        with self.assertRaises(ValueError):
            request_total({"database_wait": -1})
        with self.assertRaises(ValueError):
            candidate_total({"database_wait": 200}, "database_wait", 201)
        with self.assertRaises(ValueError):
            ebs_ceiling_screen(0, 4, 3000, 125, 7000, 100)


if __name__ == "__main__":
    unittest.main()
