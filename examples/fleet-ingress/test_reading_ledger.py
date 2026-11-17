"""Changed facts that would otherwise corrupt a fleet window."""

import unittest

from reading_ledger import accept, open_ledger, report


class ReadingLedgerTests(unittest.TestCase):
    def setUp(self):
        self.db = open_ledger()

    def tearDown(self):
        self.db.close()

    def test_late_reading_changes_event_time_window_and_replay_does_not_count_twice(self):
        expected = ['a', 'b']
        self.assertEqual(accept(self.db, 'van-17', 'van-17', 'a', 0, 5, 35), 'accepted')
        first = report(self.db, 'van-17', 0, 120, expected)
        self.assertEqual(first['status'], 'unknown')
        self.assertEqual(first['missing_expected_ids'], ['b'])
        self.assertEqual(accept(self.db, 'van-17', 'van-17', 'b', 60, 300, 85), 'accepted')
        later = report(self.db, 'van-17', 0, 120, expected)
        self.assertEqual((later['received'], later['status'], later['maximum_observed_c']), (2, 'warning', 85))
        self.assertEqual(accept(self.db, 'van-17', 'van-17', 'b', 60, 301, 85), 'duplicate')
        self.assertEqual(report(self.db, 'van-17', 0, 120, expected), later)

    def test_claimed_other_device_and_conflicting_retry_do_not_change_accepted_record(self):
        self.assertEqual(accept(self.db, 'van-17', 'van-18', 'same', 60, 90, 95), 'rejected_claim_mismatch')
        self.assertEqual(accept(self.db, 'van-17', 'van-17', 'same', 60, 91, 40), 'accepted')
        baseline = report(self.db, 'van-17', 0, 120, ['same'])
        self.assertEqual(accept(self.db, 'van-17', 'van-17', 'same', 60, 92, 99), 'rejected_conflict')
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['same']), baseline)
        self.assertEqual(accept(self.db, 'van-18', 'van-18', 'same', 60, 93, 85), 'accepted')
        self.assertEqual(report(self.db, 'van-18', 0, 120, ['same'])['status'], 'warning')

    def test_missing_or_unexpected_identity_is_not_reported_as_normal(self):
        self.assertEqual(report(self.db, 'van-17', 0, 60, ['planned'])['status'], 'unknown')
        accept(self.db, 'van-17', 'van-17', 'surprise', 0, 0, 40)
        result = report(self.db, 'van-17', 0, 60, ['planned'])
        self.assertEqual(result['missing_expected_ids'], ['planned'])
        self.assertEqual(result['unexpected_ids'], ['surprise'])
        self.assertEqual(result['status'], 'unknown')

    def test_boundary_and_invalid_inputs(self):
        accept(self.db, 'van-17', 'van-17', 'next', 60, 60, -5)
        self.assertEqual(report(self.db, 'van-17', 0, 60, [])['received'], 0)
        self.assertEqual(report(self.db, 'van-17', 0, 60, [])['status'], 'unknown')
        self.assertEqual(report(self.db, 'van-17', 60, 120, ['next'])['status'], 'normal_against_manifest')
        with self.assertRaises(ValueError):
            accept(self.db, 'van-17', 'van-17', 'bad', 20, 10, 35)
        with self.assertRaises(ValueError):
            report(self.db, 'van-17', 0, 60, ['next', 'next'])


if __name__ == '__main__':
    unittest.main()
