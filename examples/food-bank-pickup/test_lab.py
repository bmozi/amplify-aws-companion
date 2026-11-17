"""Business invariants for the local food-bank pickup journey."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest

from lab import Pickup, run


class PickupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'pickup.sqlite'
        self.pickup = Pickup(self.path)

    def test_retry_preserves_one_partner_intent_and_first_clock(self):
        first = self.pickup.submit('partner-a', 'same-key', 'depot-1', 'food_box', 0)
        replay = self.pickup.submit('partner-a', 'same-key', 'depot-1', 'food_box', 80)
        self.assertEqual(first['id'], replay['id'])
        self.assertTrue(replay['replayed'])
        self.assertEqual(self.pickup.status('partner-a', first['id'])['due_min'], 90)
        with self.assertRaisesRegex(ValueError, 'different intent'):
            self.pickup.submit('partner-a', 'same-key', 'depot-2', 'food_box', 1)
        other = self.pickup.submit('partner-b', 'same-key', 'depot-1', 'food_box', 1)
        self.assertNotEqual(other['id'], first['id'])
        with self.assertRaises(PermissionError):
            self.pickup.status('partner-b', first['id'])

    def test_one_box_survives_competing_confirmations(self):
        a = self.pickup.submit('partner-a', 'a', 'depot-1', 'food_box', 0)['id']
        b = self.pickup.submit('partner-b', 'b', 'depot-1', 'food_box', 0)['id']
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.pickup.confirm, 'operator-depot-1', key, 30)
                       for key in (a, b)]
            decisions = [future.result() for future in futures]
        self.assertEqual(sorted(decisions), ['reserved', 'unavailable'])
        self.assertEqual(self.pickup.stock(), 0)
        self.assertEqual(self.pickup.confirm('operator-depot-1', a, 80),
                         self.pickup.status('partner-a', a)['status'])
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM requests WHERE status='reserved'").fetchone()[0], 1)

    def test_ready_late_is_recorded_as_late_and_cannot_move_earlier_on_retry(self):
        key = self.pickup.submit('partner-a', 'late', 'depot-1', 'food_box', 10)['id']
        with self.assertRaises(PermissionError):
            self.pickup.label('partner-a', key)
        with self.assertRaisesRegex(ValueError, 'not been reserved'):
            self.pickup.ready('operator-depot-1', key, 20)
        self.assertEqual(self.pickup.confirm('operator-depot-1', key, 30), 'reserved')
        self.assertFalse(self.pickup.ready('operator-depot-1', key, 101))
        self.assertFalse(self.pickup.ready('operator-depot-1', key, 20))
        self.assertEqual(self.pickup.status('partner-a', key)['ready_min'], 101)
        self.assertEqual(self.pickup.status('partner-a', key)['confirmed_min'], 30)
        self.assertFalse(self.pickup.status('partner-a', key)['ready_on_time'])
        with self.assertRaises(PermissionError):
            self.pickup.label('partner-b', key)

    def test_ready_cannot_be_backdated_before_stock_confirmation(self):
        key = self.pickup.submit('partner-a', 'backdate', 'depot-1', 'food_box', 10)['id']
        with self.assertRaisesRegex(ValueError, 'precedes acceptance'):
            self.pickup.confirm('operator-depot-1', key, 9)
        self.assertEqual(self.pickup.confirm('operator-depot-1', key, 100), 'reserved')
        self.assertEqual(self.pickup.confirm('operator-depot-1', key, 20), 'reserved')
        self.assertEqual(self.pickup.status('partner-a', key)['confirmed_min'], 100)
        with self.assertRaisesRegex(ValueError, 'precedes stock confirmation'):
            self.pickup.ready('operator-depot-1', key, 20)
        self.assertEqual(self.pickup.status('partner-a', key)['status'], 'reserved')
        self.assertFalse(self.pickup.ready('operator-depot-1', key, 101))
        self.assertFalse(self.pickup.status('partner-a', key)['ready_on_time'])

    def test_reopening_service_preserves_receipt_stock_and_clock(self):
        key = self.pickup.submit('partner-a', 'persisted', 'depot-1', 'food_box', 5)['id']
        self.assertEqual(self.pickup.confirm('operator-depot-1', key, 25), 'reserved')
        reopened = Pickup(self.path)
        self.assertEqual(reopened.stock(), 0)
        self.assertEqual(reopened.status('partner-a', key)['confirmed_min'], 25)
        replay = reopened.submit('partner-a', 'persisted', 'depot-1', 'food_box', 80)
        self.assertEqual(replay['id'], key)
        self.assertTrue(replay['replayed'])
        self.assertEqual(reopened.status('partner-a', key)['due_min'], 95)

    def test_full_loopback_customer_journey(self):
        result = run()
        self.assertIsNone(result['lost_reply'][0])
        self.assertTrue(result['same_intent_replayed'])
        self.assertTrue(result['recovered_committed_id_after_restart'])
        self.assertEqual(result['pending_before_inventory'], 'pending_inventory')
        self.assertEqual(result['neighbor_read_status'], 404)
        self.assertEqual(result['partner_allocate_status'], 403)
        self.assertTrue(result['ready_on_time_at_minute_75'])
        self.assertEqual(result['backdated_ready_status'], 409)
        self.assertEqual(result['second_request_no_stock'], 'unavailable')
        self.assertEqual(result['neighbor_label_status'], 404)
        self.assertTrue(result['temporary_files_removed'])


if __name__ == '__main__':
    unittest.main()
