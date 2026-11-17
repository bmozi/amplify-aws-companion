import unittest

from plan import POOL, RECORDS, proposal, review


class GovernanceTests(unittest.TestCase):
    def test_managed_unmanaged_and_ignored_overlap_all_hold(self):
        for network, state in [('10.20.0.0/24', 'managed'),
                               ('10.20.4.0/24', 'unmanaged'),
                               ('10.20.6.0/24', 'ignored')]:
            with self.subTest(state=state):
                result = review(proposal(network), RECORDS, POOL)
                self.assertEqual(result['decision'], 'HOLD')
                self.assertEqual(result['conflicts'][0]['state'], state)

    def test_pool_rules_do_not_authorize_out_of_region_or_wrong_tag(self):
        for item in [proposal('10.20.2.0/24', region='us-east-1'),
                     proposal('10.20.2.0/24', tags={'Environment': 'dev'}),
                     proposal('10.20.2.0/25'),
                     proposal('10.21.0.0/24')]:
            with self.subTest(item=item):
                self.assertEqual(review(item, RECORDS, POOL)['decision'], 'HOLD')

    def test_other_scope_needs_independent_isolation_evidence(self):
        item = proposal('10.20.8.0/24')
        self.assertEqual(review(item, RECORDS, POOL)['decision'], 'HOLD')
        item['disconnected_domain_evidence'] = True
        self.assertEqual(review(item, RECORDS, POOL)['decision'],
                         'REVIEW_WITH_IPAM_AND_ROUTE_EVIDENCE')

    def test_clear_paper_result_never_claims_allocation(self):
        result = review(proposal('10.20.2.0/24'), RECORDS, POOL)
        self.assertEqual(result['decision'], 'REVIEW_WITH_IPAM_AND_ROUTE_EVIDENCE')

    def test_malformed_cidr_is_rejected(self):
        with self.assertRaises(ValueError):
            review(proposal('10.20.2.1/24'), RECORDS, POOL)


if __name__ == '__main__':
    unittest.main()
