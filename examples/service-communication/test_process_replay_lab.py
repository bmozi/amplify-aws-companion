import unittest

from process_replay_lab import (
    run_claim_without_result_case,
    run_race_case,
    run_restart_case,
    run_separate_copy_case,
)


class ProcessReplayTests(unittest.TestCase):
    def test_claim_survives_backend_replacement(self):
        result = run_restart_case()
        self.assertEqual(result["first_via_entry"], 200)
        self.assertEqual(result["copy_to_a"], 403)
        self.assertEqual(result["copy_to_b"], 403)
        self.assertEqual(result["copy_to_restarted_b"], 403)
        self.assertEqual(result["fresh_without_receipt"], 403)
        self.assertEqual(result["new_signed_after_restart"], 200)

    def test_claim_without_result_does_not_prove_success(self):
        self.assertEqual(run_claim_without_result_case(),
                         {"after_claim_error": 503, "retry_after_restart": 403})

    def test_two_processes_claim_one_nonce_once(self):
        self.assertEqual(run_race_case(),
                         {"accepted": 1, "rejected": 31, "other": 0})

    def test_isolated_copies_each_accept_then_union_hides_count(self):
        self.assertEqual(run_separate_copy_case(), {
            "first_a": 200, "first_b": 200,
            "repeat_a": 403, "repeat_b": 403,
            "accepted_responses": 2, "distinct_claims_after_union": 1,
        })


if __name__ == "__main__":
    unittest.main()
