import unittest

from lab import count


class ContactCostTest(unittest.TestCase):
    def setUp(self):
        self.work = dict(contact_calls=4, contact_transaction_attempts=4,
                         due_scan_evaluated_items=120, due_scan_pages=6,
                         overdue_requests_returned=8, overdue_transaction_attempts=8,
                         worklist_scan_evaluated_items=60, worklist_scan_pages=3,
                         worklist_escalations=6, worklist_open_escalations=2)

    def test_repeat_checks_and_recovery_reads_are_counted(self):
        result = count(self.work)
        self.assertEqual(result['modeled_table_read_request_units'], 196)
        self.assertEqual(result['modeled_table_write_request_units'], 40)
        self.assertEqual(result['api_calls'], {'get_item': 16, 'scan': 9,
                                                'transact_write_items': 12})
        cloud = result['boundaries']['optional_cloud_handler_candidate']
        local = result['boundaries']['local_contact_record_fixture_only']
        self.assertEqual((cloud['modeled_table_read_request_units'],
                          cloud['modeled_table_write_request_units']), (188, 32))
        self.assertEqual((local['modeled_table_read_request_units'],
                          local['modeled_table_write_request_units']), (8, 8))
        self.assertEqual(cloud['api_calls'], {'get_item': 8, 'scan': 9,
                                              'transact_write_items': 8})
        self.assertEqual(local['api_calls'], {'get_item': 8, 'scan': 0,
                                              'transact_write_items': 4})

    def test_empty_scan_pages_still_have_read_floor(self):
        self.work.update(contact_calls=0, contact_transaction_attempts=0,
                         due_scan_evaluated_items=0, due_scan_pages=2,
                         overdue_requests_returned=0, overdue_transaction_attempts=0,
                         worklist_scan_evaluated_items=0, worklist_scan_pages=1,
                         worklist_escalations=0, worklist_open_escalations=0)
        self.assertEqual(count(self.work)['modeled_table_read_request_units'], 3)

    def test_impossible_counts_rejected(self):
        self.work['overdue_transaction_attempts'] = 41
        with self.assertRaisesRegex(ValueError, 'Overdue'):
            count(self.work)

    def test_internal_conflict_retries_add_write_work(self):
        self.work['contact_transaction_attempts'] = 5
        self.work['overdue_transaction_attempts'] = 9
        result = count(self.work)
        self.assertEqual(result['modeled_table_write_request_units'], 46)
        self.assertEqual(result['api_calls']['transact_write_items'], 14)
        self.assertEqual(result['boundaries']['optional_cloud_handler_candidate']
                         ['modeled_table_write_request_units'], 36)
        self.assertEqual(result['boundaries']['local_contact_record_fixture_only']
                         ['modeled_table_write_request_units'], 10)

    def test_local_contact_calls_do_not_inflate_optional_cloud_handler(self):
        baseline = count(self.work)['boundaries']['optional_cloud_handler_candidate']
        self.work['contact_calls'] = 10
        self.work['contact_transaction_attempts'] = 10
        changed = count(self.work)
        self.assertEqual(changed['boundaries']['optional_cloud_handler_candidate'], baseline)
        self.assertEqual(changed['modeled_table_read_request_units'], 208)
        self.assertEqual(changed['modeled_table_write_request_units'], 52)

    def test_no_float_or_unknown_meter(self):
        self.work['contact_calls'] = 0.5
        with self.assertRaisesRegex(ValueError, 'nonnegative integer'):
            count(self.work)
        self.work['contact_calls'] = 1
        self.work['unpriced'] = 0
        with self.assertRaisesRegex(ValueError, 'exactly'):
            count(self.work)


if __name__ == '__main__':
    unittest.main()
