import unittest

from lab import Window, calculate, examples


class RelationalCapacityTests(unittest.TestCase):
    def test_distinguishes_large_bytes_from_many_operations(self):
        large, small, many = [calculate(window) for window in examples()]
        self.assertEqual((large["operations_per_second"], large["mib_per_second"]),
                         (1200, 128.125))
        self.assertFalse(large["above_fictional_iops_ceiling"])
        self.assertTrue(large["above_fictional_throughput_ceiling"])
        self.assertFalse(small["above_fictional_iops_ceiling"])
        self.assertFalse(small["above_fictional_throughput_ceiling"])
        self.assertTrue(many["above_fictional_iops_ceiling"])
        self.assertFalse(many["above_fictional_throughput_ceiling"])

    def test_exact_ceiling_is_not_above_and_unit_boundary_is_binary(self):
        result = calculate(Window("exact", 1000, 2000, 64, 32))
        self.assertEqual(result["mib_per_second"], 125.0)
        self.assertFalse(result["above_fictional_iops_ceiling"])
        self.assertFalse(result["above_fictional_throughput_ceiling"])

    def test_rejects_nonsense_inputs(self):
        for window in (Window("negative", -1, 0, 4, 0),
                       Window("missing read size", 1, 0, 0, 0),
                       Window("no ceiling", 1, 0, 4, 0, 0, 125)):
            with self.subTest(window=window.name):
                with self.assertRaises(ValueError):
                    calculate(window)


if __name__ == "__main__":
    unittest.main()
