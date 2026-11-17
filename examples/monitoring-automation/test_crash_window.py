import unittest
from crash_window import reconcile_timeout, simulate


class CrashWindowTest(unittest.TestCase):
    def test_crash_and_retry_outcomes(self):
        expected = {'receipt_after': 2, 'receipt_before': 0, 'provider_key': 1, 'changed_key': 2}
        for scenario, payments in expected.items():
            with self.subTest(scenario=scenario):
                result = simulate(scenario)
                self.assertEqual(result['payments'], payments)
                self.assertTrue(result['worker_receipt'])

    def test_same_key_changed_amount_is_not_marked_complete(self):
        result = simulate('changed_amount')
        self.assertEqual(result['payments'], 1)
        self.assertEqual(result['retry_outcome'], 'conflict')
        self.assertFalse(result['worker_receipt'])

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            simulate('unknown')

    def test_timeout_reconciliation_uses_evidence_and_preserves_key(self):
        cases = {'matching': 'record_confirmed_receipt', 'absent': 'retry_same_key',
                 'unavailable': 'hold_and_investigate', 'different_amount': 'hold_and_investigate'}
        for observation, action in cases.items():
            with self.subTest(observation=observation):
                self.assertEqual(reconcile_timeout(observation),
                                 {'lookup': observation, 'key_protection': 'active',
                                  'action': action, 'key': 'key-17'})

    def test_absence_does_not_authorize_retry_when_key_protection_is_uncertain(self):
        for protection in ('expired', 'unknown'):
            with self.subTest(protection=protection):
                self.assertEqual(reconcile_timeout('absent', protection)['action'], 'hold_and_investigate')

    def test_confirmed_match_can_be_recorded_after_key_expiry(self):
        self.assertEqual(reconcile_timeout('matching', 'expired')['action'], 'record_confirmed_receipt')

    def test_unknown_lookup_is_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_timeout('unknown')
        with self.assertRaises(ValueError):
            reconcile_timeout('absent', 'unverified')


if __name__ == '__main__':
    unittest.main()
