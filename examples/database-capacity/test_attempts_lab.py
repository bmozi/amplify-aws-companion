"""Check the changed-case distinctions that drive the capacity decision."""

import unittest

from attempts_lab import Attempt, capacity_for_attempt, example, worksheet


class AttemptCapacityTests(unittest.TestCase):
    def test_sample_separates_table_and_index_work(self):
        result = worksheet(example())
        self.assertEqual(result["table_write_units_per_second"], 150)
        self.assertEqual(result["gsi_write_units_per_second"], 60)
        self.assertEqual([row["gsi_write_units_per_second"] for row in result["rows"]],
                         [40, 0, 20, 0])

    def test_failed_condition_uses_existing_size_and_no_index_write(self):
        result = capacity_for_attempt(Attempt("denied new key", 3, 0, 9000,
                                              "condition_failed"))
        self.assertEqual(result, {"table_write_units_per_second": 3,
                                  "gsi_write_units_per_second": 0})

    def test_sparse_index_and_key_move_are_different(self):
        add = Attempt("becomes searchable", 1, 900, 900, "applied", 0, 400)
        move = Attempt("changes search key", 1, 900, 900, "applied", 400, 400, True)
        self.assertEqual(capacity_for_attempt(add)["gsi_write_units_per_second"], 1)
        self.assertEqual(capacity_for_attempt(move)["gsi_write_units_per_second"], 2)

    def test_rejects_unsupported_projection_and_failed_mutation(self):
        with self.assertRaises(ValueError):
            capacity_for_attempt(Attempt("too large", 1, 900, 900,
                                         "applied", 0, 1025))
        with self.assertRaises(ValueError):
            capacity_for_attempt(Attempt("false condition", 1, 900, 900,
                                         "condition_failed", 0, 400))


if __name__ == "__main__":
    unittest.main()
