"""Budget gate boundaries independent of AWS response timing and credentials."""
import importlib.util
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'publisher-budget-check.py'
SPEC = importlib.util.spec_from_file_location('publisher_budget_check', SCRIPT)
check = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(check)


class PublisherBudgetCheckTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 23, 19, 0, tzinfo=timezone.utc)
        self.budget = {
            'BudgetType': 'COST', 'TimeUnit': 'MONTHLY',
            'CostTypes': {'IncludeCredit': False, 'IncludeRefund': False},
            'BudgetLimit': {'Amount': '50', 'Unit': 'USD'},
            'CalculatedSpend': {'ActualSpend': {'Amount': '43.97', 'Unit': 'USD'}},
            'LastUpdatedTime': (self.now - timedelta(hours=7)).isoformat(),
            'TimePeriod': {'Start': '2026-09-01T00:00:00+00:00',
                           'End': '2027-01-01T00:00:00+00:00'},
        }

    def test_current_snapshot_stops_two_dollar_run_with_buffer(self):
        result = check.assess(self.budget, Decimal('2'), Decimal('5'), self.now)
        self.assertEqual(result['decision'], 'review_required')
        self.assertEqual(result['headroom_after_run_and_buffer_usd'], '-0.97')
        self.assertEqual(check.assess(self.budget, Decimal('0.5'), Decimal('5'), self.now)['decision'],
                         'within_reported_headroom')
        self.assertEqual(check.assess(self.budget, Decimal('0.5'), Decimal('5'), self.now)['actual_spend_refresh_time'],
                         'not exposed by DescribeBudget')

    def test_credit_including_budget_is_not_a_gross_guard(self):
        self.budget['CostTypes']['IncludeCredit'] = True
        with self.assertRaisesRegex(ValueError, 'exclude credits'):
            check.assess(self.budget, Decimal('1'), Decimal('5'), self.now)

    def test_old_budget_configuration_date_is_not_spend_refresh_time(self):
        self.budget['LastUpdatedTime'] = (self.now - timedelta(days=45)).isoformat()
        result = check.assess(self.budget, Decimal('0.5'), Decimal('5'), self.now)
        self.assertEqual(result['decision'], 'within_reported_headroom')

    def test_budget_period_must_cover_run(self):
        self.budget['TimePeriod']['End'] = '2026-10-01T00:00:00+00:00'
        with self.assertRaisesRegex(ValueError, 'does not cover'):
            check.assess(self.budget, Decimal('1'), Decimal('5'), self.now)

    def test_zero_estimate_or_reduced_buffer_stops(self):
        with self.assertRaisesRegex(ValueError, 'positive estimate'):
            check.assess(self.budget, Decimal('0'), Decimal('5'), self.now)
        with self.assertRaisesRegex(ValueError, 'at least USD 5'):
            check.assess(self.budget, Decimal('1'), Decimal('0'), self.now)

    def test_refunds_filters_or_unhealthy_billing_view_stop(self):
        self.budget['CostTypes']['IncludeRefund'] = True
        with self.assertRaisesRegex(ValueError, 'exclude refunds'):
            check.assess(self.budget, Decimal('1'), Decimal('5'), self.now)
        self.budget['CostTypes']['IncludeRefund'] = False
        self.budget['CostFilters'] = {'Service': ['Amazon EC2']}
        with self.assertRaisesRegex(ValueError, 'unfiltered'):
            check.assess(self.budget, Decimal('1'), Decimal('5'), self.now)
        self.budget['CostFilters'] = {}
        self.budget['HealthStatus'] = {'Status': 'UNHEALTHY'}
        with self.assertRaisesRegex(ValueError, 'unhealthy'):
            check.assess(self.budget, Decimal('1'), Decimal('5'), self.now)


if __name__ == '__main__':
    unittest.main()
