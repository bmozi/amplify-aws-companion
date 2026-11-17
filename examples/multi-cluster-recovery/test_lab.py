import copy
import json
import unittest

from lab import HERE, review


class MultiClusterRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((HERE / "case.json").read_text())

    def test_stale_data_holds_switch_even_with_healthy_containers(self):
        result = review(self.case)
        self.assertEqual(result["decision"], "hold")
        self.assertEqual(result["failed_gates"], ["data_checkpoint_within_rpo"])

    def test_old_writer_must_be_fenced(self):
        changed = copy.deepcopy(self.case)
        changed["gates"]["data_checkpoint_within_rpo"] = True
        changed["gates"]["old_writer_fenced"] = False
        self.assertEqual(review(changed)["failed_gates"], ["old_writer_fenced"])

    def test_paper_pass_never_proves_rto(self):
        changed = copy.deepcopy(self.case)
        changed["gates"]["data_checkpoint_within_rpo"] = True
        result = review(changed)
        self.assertEqual(result["decision"], "candidate_for_observed_drill")
        self.assertFalse(result["rto_proven"])

    def test_unknown_gate_is_rejected(self):
        changed = copy.deepcopy(self.case)
        changed["gates"]["target_capacity"] = "probably"
        with self.assertRaises(ValueError):
            review(changed)


if __name__ == "__main__":
    unittest.main()
