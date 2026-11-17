"""Catch incomplete whole-run comparisons, not just arithmetic syntax."""

import unittest
from decimal import Decimal

import whole_run_lab as lab


class WholeRunTests(unittest.TestCase):
    def test_same_twelve_hour_window_has_platform_and_shared_meters(self):
        ec2 = lab.estimate('ec2_asg', 12)
        fargate = lab.estimate('ecs_fargate', 12)
        eks = lab.estimate('eks_auto', 12)
        self.assertEqual(Decimal(ec2['with_25_percent_contingency_usd']), Decimal('4.775'))
        self.assertEqual(Decimal(fargate['with_25_percent_contingency_usd']), Decimal('5.275'))
        self.assertEqual(Decimal(eks['with_25_percent_contingency_usd']), Decimal('7'))
        self.assertEqual([x['within_chosen_fixture_limit'] for x in (ec2, fargate, eks)],
                         [True, False, False])
        self.assertEqual({x['chosen_fixture_limit_usd'] for x in (ec2, fargate, eks)}, {'5'})
        self.assertIn('database_hour', eks['lines_usd'])
        self.assertIn('eks_auto_node_hour', eks['lines_usd'])
        self.assertNotEqual(eks['lines_usd']['eks_cluster_hour'],
                            eks['with_25_percent_contingency_usd'])

    def test_omitted_database_or_auto_mode_meter_rejects_quote(self):
        for meter in ('database_hour', 'eks_auto_node_hour'):
            with self.subTest(meter=meter):
                rates = dict(lab.RATES)
                rates.pop(meter)
                with self.assertRaisesRegex(ValueError, 'required meter'):
                    lab.estimate('eks_auto', 12, rates)

    def test_shorter_window_changes_hours_but_not_fixed_usage(self):
        full = lab.estimate('ecs_fargate', 12)
        short = lab.estimate('ecs_fargate', 4)
        self.assertEqual(full['lines_usd']['image_storage_gb'],
                         short['lines_usd']['image_storage_gb'])
        self.assertEqual(Decimal(short['lines_usd']['fargate_vcpu_hour']), Decimal('0.60'))
        self.assertEqual(Decimal(short['lines_usd']['fargate_memory_gb_hour']), Decimal('0.30'))
        self.assertLess(float(short['with_25_percent_contingency_usd']),
                        float(full['with_25_percent_contingency_usd']))

    def test_bad_duration_or_rate_refuses_quote(self):
        with self.assertRaises(ValueError):
            lab.estimate('eks_auto', 0)
        for bad in ('-1', 'NaN'):
            rates = dict(lab.RATES)
            rates['database_hour'] = bad
            with self.assertRaisesRegex(ValueError, 'finite and nonnegative'):
                lab.estimate('ec2_asg', 12, rates)

    def test_reader_limit_changes_only_the_offline_comparison(self):
        five = lab.estimate('ecs_fargate', 12, limit_usd='5')
        six = lab.estimate('ecs_fargate', 12, limit_usd='6')
        self.assertEqual(five['lines_usd'], six['lines_usd'])
        self.assertEqual(five['with_25_percent_contingency_usd'],
                         six['with_25_percent_contingency_usd'])
        self.assertFalse(five['within_chosen_fixture_limit'])
        self.assertTrue(six['within_chosen_fixture_limit'])
        self.assertIn('not a current AWS quote', six['scope'])

    def test_bad_reader_limit_is_rejected(self):
        for bad in ('0', '-1', 'NaN', 'Infinity', 'not-a-number'):
            with self.subTest(limit=bad), self.assertRaisesRegex(ValueError, 'Limit'):
                lab.estimate('ec2_asg', 12, limit_usd=bad)


if __name__ == '__main__':
    unittest.main()
