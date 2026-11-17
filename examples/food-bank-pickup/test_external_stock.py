"""Changed-window controls for the separate stock ledger."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location('external_stock', Path(__file__).with_name('external_stock.py'))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class ExternalStockTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        self.pickup_path = root / 'pickup.sqlite'
        self.stock_path = root / 'stock.sqlite'
        self.pickup = lab.PickupCoordinator(self.pickup_path)
        self.stock = lab.StockSystem(self.stock_path)

    def tearDown(self):
        self.folder.cleanup()

    def test_lost_reply_reconciles_after_reopening_both_ledgers(self):
        self.pickup.accept('a', 'depot-1')
        self.assertEqual(self.pickup.dispatch('a', self.stock, lose_reply=True), 'stock_unknown')
        self.assertEqual(self.stock.available(), 0)
        self.pickup = lab.PickupCoordinator(self.pickup_path)
        self.stock = lab.StockSystem(self.stock_path)
        self.assertEqual(self.pickup.status('a'), 'stock_unknown')
        self.assertEqual(self.stock.reserve('reserve:a', 'a', 'depot-1'), 'reserved')
        self.assertEqual(self.pickup.reconcile('a', self.stock), 'reserved')
        self.assertEqual(self.pickup.dispatch('a', self.stock), 'reserved')
        self.assertEqual(self.stock.available(), 0)
        self.assertEqual(self.stock.lookup('reserve:a'), ('a', 'depot-1', 'reserved'))

    def test_unreachable_lookup_keeps_unknown_and_blocks_new_intent(self):
        self.pickup.accept('a', 'depot-1')
        self.pickup.dispatch('a', self.stock, lose_reply=True)
        self.assertEqual(self.pickup.reconcile('a', self.stock, query_available=False), 'stock_unknown')
        self.assertEqual(self.pickup.accept('a', 'depot-1'), 'stock_unknown')
        with self.assertRaises(ValueError):
            self.stock.reserve('reserve:a', 'different-request', 'depot-1')
        self.assertEqual(self.stock.available(), 0)

    def test_two_requests_one_box_even_when_first_reply_is_lost(self):
        self.pickup.accept('a', 'depot-1')
        self.pickup.accept('b', 'depot-1')
        self.assertEqual(self.pickup.dispatch('a', self.stock, lose_reply=True), 'stock_unknown')
        self.assertEqual(self.pickup.dispatch('b', self.stock), 'unavailable')
        self.assertEqual(self.pickup.reconcile('a', self.stock), 'reserved')
        self.assertEqual(self.stock.available(), 0)

    def test_absent_decision_does_not_become_unavailable(self):
        self.pickup.accept('a', 'depot-1')
        self.assertEqual(self.pickup.reconcile('a', self.stock), 'pending_inventory')
        self.assertEqual(self.pickup.status('a'), 'pending_inventory')
        self.assertEqual(self.stock.available(), 1)

    def test_conflicting_outcome_refused_after_recording(self):
        self.pickup.accept('a', 'depot-1')
        self.assertEqual(self.pickup.dispatch('a', self.stock), 'reserved')
        with self.assertRaises(ValueError):
            self.pickup._record('a', 'unavailable')
        self.assertEqual(self.pickup.status('a'), 'reserved')


if __name__ == '__main__':
    unittest.main()
