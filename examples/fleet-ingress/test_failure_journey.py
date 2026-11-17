import sqlite3
import tempfile
from pathlib import Path
import unittest

from failure_journey import open_journey, retry_forwarding, submit, unresolved
from reading_ledger import report


class FailureJourneyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / 'fleet.sqlite')
        self.db = open_journey(self.db_path)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def send(self, attempt, claimed='van-17', event='e1', temp=35, forwarded=True):
        return submit(self.db, attempt, 'van-17', claimed, event, 60, 600, temp,
                      forwarded=forwarded)

    def test_forwarding_failure_survives_reopen_and_reviewed_retry(self):
        self.assertEqual(self.send('a1', forwarded=False), 'forwarding_failed')
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['e1'])['received'], 0)
        self.db.close()
        self.db = open_journey(self.db_path)
        self.assertEqual(unresolved(self.db), [('a1', 'failed', 'not_seen')])
        with self.assertRaises(ValueError):
            retry_forwarding(self.db, 'a1', '', 'source inspected')
        self.assertEqual(retry_forwarding(self.db, 'a1', 'operator', 'source inspected'), 'accepted')
        self.assertEqual(unresolved(self.db), [])
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['e1'])['received'], 1)
        with self.assertRaises(ValueError):
            retry_forwarding(self.db, 'a1', 'operator', 'again')

    def test_successful_forward_can_still_be_a_business_rejection(self):
        self.assertEqual(self.send('a2', claimed='van-18'), 'rejected_claim_mismatch')
        self.assertEqual(unresolved(self.db), [('a2', 'admitted', 'rejected_claim_mismatch')])
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['e1'])['received'], 0)
        with self.assertRaises(ValueError):
            retry_forwarding(self.db, 'a2', 'operator', 'cannot fix identity by replay')

    def test_changed_replay_is_held_and_attempt_id_cannot_be_reused(self):
        self.assertEqual(self.send('a1'), 'accepted')
        self.assertEqual(self.send('a2', temp=99), 'rejected_conflict')
        self.assertEqual(self.send('a2', temp=99), 'duplicate_delivery')
        with self.assertRaises(ValueError):
            self.send('a2', temp=100)
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['e1'])['maximum_observed_c'], 35)
        self.assertEqual(unresolved(self.db), [('a2', 'admitted', 'rejected_conflict')])

    def test_receipt_failure_rolls_back_the_accepted_reading(self):
        self.db.execute('''CREATE TRIGGER stop_receipt BEFORE INSERT ON deliveries
                           WHEN NEW.attempt_id = 'bad'
                           BEGIN SELECT RAISE(ABORT, 'receipt failed'); END''')
        with self.assertRaises(sqlite3.IntegrityError):
            self.send('bad')
        self.assertEqual(report(self.db, 'van-17', 0, 120, ['e1'])['received'], 0)


if __name__ == '__main__':
    unittest.main()
