import unittest
from dataclasses import replace
from lab import Candidate, CarbonObservation, compare_synthetic_carbon, shortlist


BASE = Candidate('region-alpha', True, True, 80, True, 420, 12_000,
                 CarbonObservation(80, 'toy-method', 'same-whole-path', 'one-month', 'repairs-v1'))


class RegionShortlistTests(unittest.TestCase):
    def test_lower_toy_carbon_does_not_override_residency_or_service_gap(self):
        lower = replace(BASE, label='region-beta', residency_ok=False,
                        carbon=replace(BASE.carbon, value=50))
        self.assertEqual(shortlist(lower)[0], 'reject')
        self.assertIn('residency', shortlist(lower)[1])
        self.assertIsNone(compare_synthetic_carbon(BASE, lower))
        no_service = replace(BASE, services_ok=False)
        self.assertIn('required services', shortlist(no_service)[1])

    def test_missing_transfer_or_price_is_pending_not_zero(self):
        no_transfer = replace(BASE, transfer_included=False)
        no_price = replace(BASE, estimated_run_cents=None)
        self.assertEqual(shortlist(no_transfer)[0], 'pending')
        self.assertIn('transfer and replication in estimate', shortlist(no_transfer)[2])
        self.assertEqual(shortlist(no_price)[0], 'pending')
        self.assertIn('complete run estimate', shortlist(no_price)[2])

    def test_run_and_reserve_limits_are_hard_gates_in_toy_case(self):
        self.assertIn('run limit', shortlist(replace(BASE, estimated_run_cents=501))[1])
        self.assertIn('credit reserve', shortlist(replace(BASE, projected_credit_reserve_cents=9_999))[1])
        self.assertEqual(shortlist(replace(BASE, estimated_run_cents=500,
                                           projected_credit_reserve_cents=10_000))[0],
                         'paper_shortlist')

    def test_changed_case_uses_selected_limits_for_both_candidates(self):
        second = replace(BASE, label='region-delta', estimated_run_cents=600,
                         projected_credit_reserve_cents=8_000,
                         carbon=replace(BASE.carbon, value=50))
        self.assertEqual(shortlist(second)[0], 'reject')
        self.assertEqual(shortlist(second, max_run_cents=700,
                                   min_reserve_cents=7_500)[0], 'paper_shortlist')
        self.assertIsNone(compare_synthetic_carbon(BASE, second))
        self.assertEqual(compare_synthetic_carbon(BASE, second, max_run_cents=700,
                                                  min_reserve_cents=7_500), 'region-delta')
        with self.assertRaises(ValueError):
            shortlist(BASE, max_run_cents=-1)

    def test_carbon_methods_or_workloads_must_match(self):
        different = replace(BASE, label='region-beta', carbon=replace(BASE.carbon, value=50,
                                                                       method='toy-method-B'))
        self.assertIsNone(compare_synthetic_carbon(BASE, different))
        different = replace(different, carbon=replace(BASE.carbon, value=50,
                                                       workload='unmatched-volume'))
        self.assertIsNone(compare_synthetic_carbon(BASE, different))

    def test_comparable_toy_values_only_order_numbers(self):
        lower = replace(BASE, label='region-beta', carbon=replace(BASE.carbon, value=50))
        self.assertEqual(shortlist(lower)[0], 'paper_shortlist')
        self.assertEqual(compare_synthetic_carbon(BASE, lower), 'region-beta')
        self.assertEqual(compare_synthetic_carbon(BASE, replace(lower, carbon=BASE.carbon)),
                         'equal supplied toy values')

    def test_unknown_residency_and_latency_stay_pending(self):
        unknown = replace(BASE, residency_ok=None, latency_ms=None)
        self.assertEqual(shortlist(unknown)[0], 'pending')
        self.assertIn('residency', shortlist(unknown)[2])
        self.assertIn('customer latency', shortlist(unknown)[2])


if __name__ == '__main__':
    unittest.main()
