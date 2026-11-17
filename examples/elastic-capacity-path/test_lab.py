import unittest
from decimal import Decimal as D
from lab import Path, evaluate


class CapacityPathTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(D(60), D("0.1"), D("0.4"), 2, D(20), D(28), D(8))

    def test_added_worker_does_not_fix_database_read_limit(self):
        self.assertEqual(evaluate(self.base)["exceeded"], ("database_reads",))
        more_workers = Path(D(60), D("0.1"), D("0.4"), 3, D(20), D(28), D(8))
        self.assertEqual(evaluate(more_workers)["exceeded"], ("database_reads",))

    def test_safe_hits_reduce_only_read_and_origin_work(self):
        improved = Path(D(60), D("0.1"), D("0.5"), 2, D(20), D(28), D(8))
        result = evaluate(improved)
        self.assertEqual((result["cache_hits"], result["origin_requests"], result["database_reads"], result["database_writes"]),
                         (D(30), D(30), D(24), D(6)))
        self.assertTrue(result["fits_steady_snapshot"])

    def test_writes_cannot_be_declared_shared_cache_hits(self):
        invalid = Path(D(60), D("0.3"), D("0.8"), 2, D(20), D(28), D(8))
        with self.assertRaises(ValueError):
            evaluate(invalid)

    def test_zero_ready_workers_is_not_a_free_pass(self):
        stopped = Path(D(60), D("0.1"), D("0.4"), 0, D(20), D(28), D(8))
        self.assertIn("application", evaluate(stopped)["exceeded"])


if __name__ == "__main__":
    unittest.main()
