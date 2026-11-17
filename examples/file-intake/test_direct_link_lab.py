"""Customer-path negative controls for the fictional second file route."""

import unittest

from direct_link_lab import run


class DirectLinkTests(unittest.TestCase):
    def test_app_withdrawal_does_not_revoke_independent_copy(self):
        result = run()
        self.assertEqual(result['after_upload'],
                         {'owner_route': 404, 'shared_link': 200, 'wrong_link': 404})
        self.assertEqual(result['after_scan'], {'owner_route': 404, 'shared_link': 200})
        self.assertEqual(result['approved_owner_read'], 200)
        self.assertEqual(result['after_withdrawal'],
                         {'owner_route': 404, 'shared_link': 200})
        self.assertEqual(result['after_copy_retirement'], 410)
        self.assertTrue(result['temporary_resources_removed'])


if __name__ == '__main__':
    unittest.main()
