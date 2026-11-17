"""Independent-process, durable-ledger fault exercise checks."""

import unittest

from process_lab import run_concurrent_retry, run_experiment


class ProcessLabTests(unittest.TestCase):
    def test_committed_booking_survives_restart_and_same_id_retry(self):
        outcome = run_experiment()
        self.assertEqual(outcome["first_customer_outcome"], "timeout")
        self.assertTrue(outcome["committed_before_worker_stop"])
        self.assertTrue(outcome["first_worker_stopped"])
        self.assertTrue(outcome["worker_pids_differ"])
        self.assertEqual(outcome["fault_request_records"], 1)
        self.assertTrue(outcome["customer_conflict_rejected"])
        self.assertTrue(outcome["new_probes_correct"])
        self.assertTrue(outcome["hypothesis_met"])

    def test_new_worker_does_not_repair_broken_retry_contract(self):
        outcome = run_experiment(unsafe_retry=True)
        self.assertTrue(outcome["committed_before_worker_stop"])
        self.assertEqual(outcome["fault_request_records"], 2)
        self.assertTrue(outcome["new_probes_correct"])
        self.assertFalse(outcome["hypothesis_met"])

    def test_two_workers_racing_same_id_keep_one_booking(self):
        outcome = run_concurrent_retry()
        self.assertTrue(outcome["worker_pids_differ"])
        self.assertEqual(outcome["record_count"], 1)
        self.assertTrue(outcome["same_booking"])


if __name__ == "__main__":
    unittest.main()
