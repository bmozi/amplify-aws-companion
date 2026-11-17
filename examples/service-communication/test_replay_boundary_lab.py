from concurrent.futures import ThreadPoolExecutor
import unittest

from replay_boundary_lab import NonceLedger, run_case


class ReplayBoundaryTests(unittest.TestCase):
    def test_separate_backends_accept_the_same_copied_receipt(self):
        result = run_case(False)
        self.assertEqual(result["first_via_entry"], 200)
        self.assertEqual(result["copied_to_same_backend"], 403)
        self.assertEqual(result["copied_to_second_backend"], 200)
        self.assertEqual(result["direct_without_receipt"], 403)

    def test_shared_atomic_ledger_rejects_second_use(self):
        result = run_case(True)
        self.assertEqual(result["first_via_entry"], 200)
        self.assertEqual(result["copied_to_same_backend"], 403)
        self.assertEqual(result["copied_to_second_backend"], 403)
        # A new signed nonce is not business idempotency; both reads succeed.
        self.assertEqual(result["new_entry_request"], 200)

    def test_concurrent_claim_has_one_local_winner(self):
        ledger = NonceLedger()
        with ThreadPoolExecutor(max_workers=16) as pool:
            accepted = list(pool.map(ledger.claim, ["same-nonce"] * 64))
        self.assertEqual(sum(accepted), 1)


if __name__ == "__main__":
    unittest.main()
