import unittest

from lab import simulate


CASE = {
    'now': 3602, 'other_table_items': 37,
    'requests': [
        {'id': 'R1', 'accepted_at': 0, 'contact_at': None},
        {'id': 'R2', 'accepted_at': 0, 'contact_at': 3500},
        {'id': 'R3', 'accepted_at': 0, 'contact_at': None},
        {'id': 'R4', 'accepted_at': 3550, 'contact_at': None},
    ], 'index_visible': ['R2', 'R3'],
}


class ContactDiscoveryTest(unittest.TestCase):
    def test_index_lag_misses_due_and_stale_entry_is_rejected(self):
        result = simulate(CASE)
        self.assertEqual(result['open_work'], ['R3'])
        self.assertEqual(result['missed_due_without_reconciliation'], ['R1'])
        self.assertEqual(result['stale_index_candidates_rejected_by_base_read'], ['R2'])
        self.assertEqual(result['work_counts_not_request_units']['scan_evaluated_items'], 0)

    def test_full_scan_recovers_missing_due_work_and_reads_unrelated_items(self):
        result = simulate(CASE, reconcile=True)
        self.assertEqual(result['open_work'], ['R1', 'R3'])
        self.assertEqual(result['missed_due_without_reconciliation'], [])
        self.assertEqual(result['work_counts_not_request_units']['scan_evaluated_items'], 41)
        self.assertEqual(result['work_counts_not_request_units']['scan_pages_at_limit_20'], 3)
        self.assertEqual(result['work_counts_not_request_units']['base_gets'], 2)

    def test_contact_after_base_read_is_rechecked_at_final_condition(self):
        result = simulate(CASE, reconcile=True, contact_before_commit={'R3': 3601})
        self.assertEqual(result['open_work'], ['R1'])
        self.assertEqual(result['escalation_records'], ['R1', 'R3'])
        self.assertEqual(result['late_contacts_with_historical_breach'], ['R3'])

    def test_exact_deadline_is_not_overdue(self):
        case = dict(CASE, now=3600)
        result = simulate(case, reconcile=True)
        self.assertEqual(result['open_work'], [])

    def test_existing_late_contact_keeps_breach_without_open_work(self):
        requests = [dict(item) for item in CASE['requests']]
        requests[2]['contact_at'] = 3601
        case = dict(CASE, requests=requests)
        result = simulate(case)
        self.assertEqual(result['escalation_records'], ['R3'])
        self.assertEqual(result['open_work'], [])
        self.assertEqual(result['late_contacts_with_historical_breach'], ['R3'])

    def test_invalid_duplicate_and_unknown_index_key_refused(self):
        case = dict(CASE, index_visible=['R2', 'R2'])
        with self.assertRaisesRegex(ValueError, 'index_visible'):
            simulate(case)
        case['index_visible'] = ['UNKNOWN']
        with self.assertRaisesRegex(ValueError, 'index_visible'):
            simulate(case)


if __name__ == '__main__':
    unittest.main()
