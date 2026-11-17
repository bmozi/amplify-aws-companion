"""Changed-condition tests for a dashboard decision, not dashboard rendering."""
import unittest

from decision_lab import fixture_database, review_decision
from lab import report


class DashboardDecisionTest(unittest.TestCase):
    def setUp(self):
        self.db = fixture_database()
        self.expected = [('A','1'),('A','2'),('A','3')]
        self.before = report(self.db,'A')
        self.db.execute("UPDATE orders SET delivered=95 WHERE shop='A' AND id='3'")
        self.after = report(self.db,'A')
        self.inputs = dict(expected_keys=self.expected, allowed_shops=['A'],
                           displayed_rate='2/3', latest_source_change_minute=490,
                           import_success_minute=500, opened_minute=540)

    def tearDown(self):
        self.db.close()

    def test_ready_means_human_review_not_automatic_staffing(self):
        result = review_decision(self.after, **self.inputs)
        self.assertEqual(result['status'], 'ready_for_human_review')
        self.assertFalse(result['staffing_action_taken'])
        self.assertEqual((result['confirmed_on_time'],result['eligible_orders']), (2,3))

    def test_page_open_does_not_repair_a_stale_import(self):
        inputs = dict(self.inputs, import_success_minute=480)
        result = review_decision(self.after, **inputs)
        self.assertIn('source_newer_than_import', result['reasons'])
        self.assertFalse(result['staffing_action_taken'])
        inputs = dict(self.inputs, opened_minute=600)
        self.assertIn('import_too_old_for_decision',
                      review_decision(self.after, **inputs)['reasons'])

    def test_known_only_fraction_hides_missing_outcomes(self):
        inputs = dict(self.inputs, displayed_rate='1/2')
        result = review_decision(self.before, **inputs)
        self.assertIn('delivery_outcomes_missing', result['reasons'])
        self.assertIn('displayed_denominator_or_value_mismatch', result['reasons'])
        self.assertEqual(result['order_level_rate'], '1/3')

    def test_correct_looking_total_cannot_replace_expected_order_ids(self):
        false_report = dict(self.after, keys=[('A','1'),('A','1'),('A','2')])
        result = review_decision(false_report, **self.inputs)
        self.assertIn('order_identity_mismatch', result['reasons'])
        self.assertEqual(result['order_level_rate'], '2/3')

    def test_filter_is_not_even_a_fixture_scope_if_b_is_included(self):
        false_report = dict(self.after, keys=self.expected+[('B','1')])
        result = review_decision(false_report, **self.inputs)
        self.assertIn('fixture_scope_mismatch', result['reasons'])
        self.assertIn('order_identity_mismatch', result['reasons'])
        self.assertIn('no authenticated service denial', result['scope_evidence'])

    def test_empty_period_has_no_green_rate(self):
        empty = report(self.db, 'missing')
        inputs = dict(self.inputs, expected_keys=[], displayed_rate='0')
        result = review_decision(empty, **inputs)
        self.assertIn('no_qualifying_orders', result['reasons'])
        self.assertIsNone(result['order_level_rate'])

    def test_invalid_time_order_refused(self):
        with self.assertRaises(ValueError):
            review_decision(self.after, **dict(self.inputs, import_success_minute=541))
        with self.assertRaises(ValueError):
            review_decision(self.after, **dict(self.inputs, displayed_rate=2/3))


if __name__ == '__main__':
    unittest.main()
