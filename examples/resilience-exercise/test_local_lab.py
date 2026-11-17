"""Observe a real loopback timeout, retry, stop and business-result check."""

import unittest
from urllib.error import HTTPError
import time

from local_lab import BookingState, WORKER, audit, book, local_server, run_experiment


class LocalResilienceExperimentTests(unittest.TestCase):
    def test_timeout_retry_keeps_one_booking_and_new_work_recovers(self):
        outcome = run_experiment()
        self.assertEqual(outcome["first_customer_outcome"], "timeout")
        self.assertEqual(outcome["fault_request_records"], 1)
        self.assertTrue(outcome["new_probes_correct"])
        self.assertTrue(outcome["fault_stopped"])
        self.assertTrue(outcome["hypothesis_met"])
        self.assertGreaterEqual(outcome["observed_failure_to_second_probe_seconds"], 0)

    def test_stopping_delay_does_not_repair_duplicate_business_effect(self):
        outcome = run_experiment(unsafe_retry=True)
        self.assertEqual(outcome["fault_request_records"], 2)
        self.assertTrue(outcome["fault_stopped"])
        self.assertFalse(outcome["hypothesis_met"])

    def test_wrong_target_or_blind_observer_cannot_start(self):
        state = BookingState()
        for targets, age, ready in [(["booking-shared-1"], 0, True),
                                    ([WORKER, "booking-shared-1"], 0, True),
                                    ([WORKER], 21, True), ([WORKER], 0, False)]:
            with self.subTest(targets=targets, age=age, ready=ready):
                with self.assertRaises(ValueError):
                    state.start_fault(targets, observer_age_seconds=age, recovery_ready=ready)
                self.assertFalse(state.snapshot()["fault_active"])

    def test_retry_identity_cannot_switch_customer(self):
        state = BookingState()
        with local_server(state) as url:
            original = book(url, "same", "Alex")
            with self.assertRaises(HTTPError) as raised:
                book(url, "same", "Sam")
            self.assertEqual(raised.exception.code, 409)
            rows = audit(url)["rows"]
            self.assertEqual(rows, [original])

    def test_attempt_limit_ends_fault_even_without_operator_stop(self):
        state = BookingState()
        with local_server(state) as url:
            state.start_fault([WORKER], observer_age_seconds=0, recovery_ready=True,
                              delay_seconds=0.01, duration_seconds=60, max_attempts=1)
            book(url, "one", "Alex")
            book(url, "two", "Sam")
            self.assertFalse(audit(url)["fault_active"])

    def test_duration_limit_ends_fault_when_no_requests_arrive(self):
        state = BookingState()
        state.start_fault([WORKER], observer_age_seconds=0, recovery_ready=True,
                          duration_seconds=0.02)
        time.sleep(0.03)
        self.assertFalse(state.snapshot()["fault_active"])


if __name__ == "__main__":
    unittest.main()
