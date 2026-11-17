import unittest
from dataclasses import replace

from lab import Delivery, Probe, Work, assess, sample


class OperationsClosureTests(unittest.TestCase):
    def test_recovered_work_and_repaired_alert_path(self):
        result = assess(**sample())
        self.assertTrue(result['operations_handoff_complete'])
        self.assertEqual((result['unique_transitions'], result['delivery_attempts']), (2, 3))

    def test_green_alarm_does_not_finish_accepted_work(self):
        case = sample()
        case['work'] = [replace(case['work'][0], completed_minute=None)]
        result = assess(**case)
        self.assertFalse(result['customer_recovered'])
        self.assertIn('accepted_work_incomplete', result['customer_gaps'])

    def test_stale_or_same_run_probe_cannot_certify_customer(self):
        case = sample()
        case['probes'] = [replace(p, measured_minute=p.measured_minute - 10) for p in case['probes']]
        self.assertFalse(assess(**case)['customer_recovered'])
        case = sample()
        case['probes'] = [case['probes'][0], replace(case['probes'][1], run_id='p1')]
        self.assertFalse(assess(**case)['customer_recovered'])

    def test_wrong_scope_probe_does_not_fill_gap(self):
        case = sample()
        case['probes'] = [case['probes'][0], replace(case['probes'][1], region='us-west-2')]
        self.assertFalse(assess(**case)['customer_recovered'])

    def test_missing_intake_row_blocks_reconciliation(self):
        case = sample()
        case['accepted_ids'] = {'booking-7', 'booking-8'}
        self.assertIn('accepted_work_inventory_unreconciled', assess(**case)['customer_gaps'])

    def test_notification_failure_needs_operational_followup(self):
        case = sample()
        case['deliveries'] = [Delivery('alarm-enter-1', False), Delivery('alarm-ok-1', True)]
        result = assess(**case)
        self.assertTrue(result['customer_recovered'])
        self.assertFalse(result['operations_handoff_complete'])
        self.assertIn('notification_path_unverified', result['operations_gaps'])

    def test_new_transition_is_not_hidden_as_duplicate(self):
        case = sample()
        case['deliveries'].append(Delivery('alarm-enter-2', False))
        result = assess(**case)
        self.assertEqual(result['unique_transitions'], 3)
        self.assertFalse(result['operations_handoff_complete'])

    def test_owner_and_alarm_are_separate_from_customer_result(self):
        case = sample()
        case['owner'] = ''
        case['current_alarm'] = 'ALARM'
        result = assess(**case)
        self.assertTrue(result['customer_recovered'])
        self.assertEqual(result['operations_gaps'], ['no_named_owner', 'alarm_not_ok'])


if __name__ == '__main__':
    unittest.main()
