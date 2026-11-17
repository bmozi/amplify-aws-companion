"""Changed-condition controls for synthetic receipt reconciliation."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('contact_reconcile', HERE / 'reconcile.py')
reconcile_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile_module)


def fixture():
    return json.loads((HERE / 'synthetic-receipts.json').read_text())


class ReceiptReconciliationTests(unittest.TestCase):
    def test_retries_and_canceled_unknown_are_preserved_without_double_adding_total(self):
        result = reconcile_module.reconcile(fixture())
        self.assertEqual(4, result['invocations_seen'])
        self.assertEqual([2, 1, 1], [p['pages_with_responses'] for p in result['passes']])
        self.assertTrue(result['supplied_page_chains_complete'])
        self.assertEqual('20', result['observed_read_capacity_units'])
        self.assertEqual('2', result['observed_write_capacity_units'])
        self.assertEqual('23.5', result['observed_total_capacity_units'])
        self.assertEqual(1, result['unreported_operations'])
        self.assertEqual(2, result['canceled_operations'])
        self.assertFalse(result['supplied_numeric_observations_complete'])
        self.assertFalse(result['bill_reconciled'])
        self.assertFalse(result['approved_to_deploy'])
        self.assertNotIn('fictional-page-boundary', json.dumps(result))

    def test_unfinished_page_chain_is_not_complete(self):
        data = fixture()
        data['invocations'].pop(1)
        result = reconcile_module.reconcile(data)
        self.assertFalse(result['supplied_page_chains_complete'])
        self.assertFalse(result['supplied_numeric_observations_complete'])

    def test_lost_response_is_unknown_even_after_a_prior_page(self):
        data = fixture()
        data['invocations'][1] = {
            'invocation_id': 'due-2', 'pass_id': 'due-first',
            'action': 'check_due', 'requested_cursor': {'pk': 'fictional-page-boundary'},
            'status': 'failed_no_response',
        }
        result = reconcile_module.reconcile(data)
        self.assertEqual(1, result['failed_invocations_without_response'])
        self.assertFalse(result['supplied_page_chains_complete'])

    def test_wrong_cursor_and_duplicate_invocation_are_rejected(self):
        data = fixture()
        data['invocations'][1]['requested_cursor'] = {'pk': 'wrong'}
        with self.assertRaisesRegex(ValueError, 'cursor'):
            reconcile_module.reconcile(data)
        data = fixture()
        data['invocations'][1]['invocation_id'] = 'due-1'
        with self.assertRaisesRegex(ValueError, 'unique'):
            reconcile_module.reconcile(data)

    def test_nonfinite_negative_and_misreported_capacity_are_rejected(self):
        for bad in ('NaN', '-1', True):
            with self.subTest(bad=bad):
                data = fixture()
                data['invocations'][0]['response']['capacity_observations'][0][
                    'read_capacity_units'] = bad
                with self.assertRaisesRegex(ValueError, 'nonnegative finite'):
                    reconcile_module.reconcile(data)
        data = fixture()
        row = data['invocations'][0]['response']['capacity_observations'][0]
        row['reported'] = False
        with self.assertRaisesRegex(ValueError, 'Reported flag'):
            reconcile_module.reconcile(data)

    def test_total_only_is_kept_unallocated_and_customer_fields_not_emitted(self):
        data = fixture()
        data['invocations'][0]['response']['customer_text'] = 'private fictional request'
        result = reconcile_module.reconcile(data)
        self.assertEqual('23.5', result['observed_total_capacity_units'])
        self.assertEqual('20', result['observed_read_capacity_units'])
        self.assertNotIn('private fictional request', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
