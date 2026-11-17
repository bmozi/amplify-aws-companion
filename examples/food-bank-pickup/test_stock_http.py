"""Exercise the post-commit lost-reply window across two local processes."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location('stock_http', Path(__file__).with_name('stock_http.py'))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class StockHttpTests(unittest.TestCase):
    def test_restart_and_authoritative_lookup_after_reply_loss(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            result = lab.run(root / 'pickup.sqlite', root / 'stock.sqlite', root / 'ready')
            self.assertEqual(result['after_lost_http_reply'], 'stock_unknown')
            self.assertEqual(result['while_provider_down'], 'stock_unknown')
            self.assertEqual(result['after_new_process_lookup'], 'reserved')
            self.assertEqual(result['same_id_replay'], 'reserved')
            self.assertEqual(result['second_request'], 'unavailable')
            self.assertEqual(result['remaining_boxes'], 0)
            self.assertTrue(result['provider_process_changed'])

    def test_wrong_intent_is_rejected_after_provider_restart(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            stock_path, ready_path = root / 'stock.sqlite', root / 'ready'
            with lab.provider(stock_path, ready_path) as (_, stock):
                self.assertEqual(stock.reserve('fixed-id', 'a', 'depot-1'), 'reserved')
            with lab.provider(stock_path, ready_path) as (_, stock):
                with self.assertRaises(ValueError):
                    stock.reserve('fixed-id', 'different-request', 'depot-1')
                self.assertEqual(stock.lookup('fixed-id'), ('a', 'depot-1', 'reserved'))
                self.assertEqual(stock.available(), 0)

    def test_unreachable_before_reserve_does_not_become_false_unavailable(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pickup = lab.PickupCoordinator(root / 'pickup.sqlite')
            pickup.accept('a', 'depot-1')
            with lab.provider(root / 'stock.sqlite', root / 'ready') as (_, stock):
                port = int(stock.base.rsplit(':', 1)[1])
            offline = lab.StockHttpClient(port)
            self.assertEqual(pickup.dispatch('a', offline), 'stock_unknown')
            with lab.provider(root / 'stock.sqlite', root / 'ready') as (_, stock):
                self.assertIsNone(stock.lookup('reserve:a'))
                self.assertEqual(pickup.reconcile('a', stock), 'stock_unknown')
                self.assertEqual(stock.available(), 1)

    def test_missing_and_wrong_token_cannot_reserve_or_read_stock(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            with lab.provider(root / 'stock.sqlite', root / 'ready') as (_, stock):
                port = int(stock.base.rsplit(':', 1)[1])
                for caller in (lab.StockHttpClient(port),
                               lab.StockHttpClient(port, 'wrong-local-token')):
                    self.assertEqual(caller.request('/reserve', {
                        'operation_id': 'reserve:stolen', 'request_id': 'stolen',
                        'depot': 'depot-1', 'drop_reply': False,
                    }), (401, {'error': 'unauthorized'}))
                    self.assertEqual(caller.request('/decisions/reserve%3Astolen'),
                                     (401, {'error': 'unauthorized'}))
                    self.assertEqual(caller.request('/availability'),
                                     (401, {'error': 'unauthorized'}))
                self.assertEqual(stock.available(), 1)
                self.assertIsNone(stock.lookup('reserve:stolen'))
                self.assertEqual(stock.reserve('reserve:real', 'real', 'depot-1'), 'reserved')
                self.assertEqual(stock.lookup('reserve:real'), ('real', 'depot-1', 'reserved'))
                self.assertEqual(lab.StockHttpClient(port, 'wrong-local-token').request(
                    '/decisions/reserve%3Areal'), (401, {'error': 'unauthorized'}))

    def test_replacement_provider_rejects_previous_process_token(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            stock_path, ready_path = root / 'stock.sqlite', root / 'ready'
            with lab.provider(stock_path, ready_path) as (_, first):
                old_token = first.token
                self.assertEqual(first.reserve('stable-id', 'a', 'depot-1'), 'reserved')
            with lab.provider(stock_path, ready_path) as (_, second):
                port = int(second.base.rsplit(':', 1)[1])
                stale = lab.StockHttpClient(port, old_token)
                self.assertEqual(stale.request('/decisions/stable-id'),
                                 (401, {'error': 'unauthorized'}))
                self.assertEqual(second.lookup('stable-id'), ('a', 'depot-1', 'reserved'))


if __name__ == '__main__':
    unittest.main()
