import unittest

from gate import Evidence, decide


class RecoveryGateTests(unittest.TestCase):
    def test_all_evidence_and_automatic_policy_allow_cutover(self):
        result, _ = decide(Evidence(True, True, True, True, True, True, True, True))
        self.assertEqual(result, 'CUTOVER')

    def test_stale_observer_blocks_even_when_everything_else_passes(self):
        result, reasons = decide(Evidence(True, False, True, True, True, True, True, True))
        self.assertEqual(result, 'NO_GO')
        self.assertIn('observer evidence is stale or unavailable', reasons)

    def test_old_writer_must_be_fenced(self):
        result, reasons = decide(Evidence(True, True, True, True, True, False, True, True))
        self.assertEqual(result, 'NO_GO')
        self.assertIn('old writer is not fenced', reasons)

    def test_business_reconciliation_is_required(self):
        result, reasons = decide(Evidence(True, True, True, True, False, True, True, True))
        self.assertEqual(result, 'NO_GO')
        self.assertIn('business records are not reconciled', reasons)

    def test_manual_policy_waits_for_approval(self):
        result, _ = decide(Evidence(True, True, True, True, True, True, True, False))
        self.assertEqual(result, 'WAIT_FOR_APPROVAL')

    def test_explicit_approval_opens_manual_gate_after_all_checks(self):
        result, _ = decide(Evidence(True, True, True, True, True, True, True, False, True))
        self.assertEqual(result, 'CUTOVER')

    def test_failed_trigger_cannot_start_recovery_cutover(self):
        result, reasons = decide(Evidence(False, True, True, True, True, True, True, True))
        self.assertEqual(result, 'NO_GO')
        self.assertIn('incident trigger is not confirmed', reasons)


if __name__ == '__main__':
    unittest.main()
