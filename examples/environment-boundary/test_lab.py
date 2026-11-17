"""Changed-destination negative controls for the fictional bundle audit."""

from copy import deepcopy
import unittest

from lab import DESTINATIONS, audit, fixture


class EnvironmentBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.bundles, self.approved = fixture()

    def test_declared_preview_sharing_is_visible_not_called_isolation(self):
        result = audit(self.bundles, self.approved)
        self.assertEqual(result['result'], 'checked_fields_match_supplied_plan')
        shared = [s for s in result['sharing'] if s['frontends'] == ['practice', 'preview']]
        self.assertEqual({s['component'] for s in shared}, DESTINATIONS)
        self.assertEqual({s['kind'] for s in shared}, {'declared_shared'})

    def test_practice_label_does_not_excuse_copied_live_backend(self):
        changed = deepcopy(self.bundles)
        changed['practice']['outputs'] = deepcopy(changed['live']['outputs'])
        changed['practice']['external'] = deepcopy(changed['live']['external'])
        result = audit(changed, self.approved)
        self.assertEqual(result['result'], 'review_required')
        self.assertTrue(DESTINATIONS.issubset({m.get('component') for m in result['mismatches']}))

    def test_one_live_data_endpoint_is_detected_inside_mixed_bundle(self):
        changed = deepcopy(self.bundles)
        changed['practice']['outputs']['data']['url'] = changed['live']['outputs']['data']['url']
        result = audit(changed, self.approved)
        self.assertIn({'scope': 'practice', 'component': 'data',
                       'reason': 'missing or different destination'}, result['mismatches'])
        self.assertTrue(any(s['component'] == 'data' and s['kind'] == 'unexpected_shared'
                            for s in result['sharing']))

    def test_user_pool_client_or_data_auth_change_requires_review(self):
        changed = deepcopy(self.bundles)
        changed['practice']['outputs']['auth']['user_pool_client_id'] = 'liveClient'
        changed['practice']['outputs']['data']['default_authorization_type'] = 'API_KEY'
        result = audit(changed, self.approved)
        self.assertEqual(result['result'], 'review_required')
        self.assertTrue({'user_pool_client', 'data_default_auth'}.issubset(
            {m.get('component') for m in result['mismatches']}))

    def test_missing_destination_and_undeclared_bundle_require_review(self):
        changed = deepcopy(self.bundles)
        del changed['practice']['outputs']['storage']['bucket_name']
        changed['surprise'] = deepcopy(changed['practice'])
        result = audit(changed, self.approved)
        self.assertEqual(result['result'], 'review_required')
        self.assertTrue(any(m['scope'] == 'inventory' for m in result['mismatches']))
        self.assertTrue(any(m.get('component') == 'files' for m in result['mismatches']))


if __name__ == '__main__':
    unittest.main()
