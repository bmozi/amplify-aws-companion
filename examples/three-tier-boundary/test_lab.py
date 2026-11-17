"""Behavior checks for the synthetic two-worker request path."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('three_tier_lab', Path(__file__).with_name('lab.py'))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class TwoWorkerBoundaryTests(unittest.TestCase):
    def test_shared_record_survives_route_to_other_worker_but_local_receipt_does_not(self):
        with lab.running_fixture() as (base, _, _):
            status, created = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
            self.assertEqual(status, 201)
            ident = created['request_id']
            local_status, local = lab.request(base, 'GET', '/local/' + ident)
            self.assertEqual((local_status, local['worker']), (404, 'worker-b'))
            reads = [lab.request(base, 'GET', '/repairs/' + ident) for _ in range(2)]
            self.assertEqual({value['worker'] for _, value in reads}, {'worker-a', 'worker-b'})
            self.assertTrue(all(code == 200 and value['issue'] == 'pump' for code, value in reads))

    def test_other_actor_and_missing_record_look_the_same_to_caller(self):
        with lab.running_fixture() as (base, _, _):
            _, created = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
            denied = lab.request(base, 'GET', '/repairs/' + created['request_id'], actor='fixture-bob')
            missing = lab.request(base, 'GET', '/repairs/' + 'not-an-id', actor='fixture-bob')
            self.assertEqual(denied[0], 404)
            self.assertEqual(missing[0], 404)
            self.assertEqual(denied[1]['error'], missing[1]['error'])

    def test_store_slot_remains_the_limit_with_two_healthy_workers(self):
        with lab.running_fixture() as (base, store, router):
            with store.hold_slot():
                code, result = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
                self.assertEqual((code, result['error']), (503, 'store_busy'))
                self.assertEqual(router.healthy, [True, True])
            code, _ = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
            self.assertEqual(code, 201)

    def test_router_skips_one_unhealthy_worker_but_toy_fails_closed_when_none(self):
        with lab.running_fixture() as (base, _, router):
            router.healthy[0] = False
            code, result = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
            self.assertEqual((code, result['worker']), (201, 'worker-b'))
            router.healthy[1] = False
            code, result = lab.request(base, 'GET', '/repairs/' + result['request_id'])
            self.assertEqual((code, result['error']), (503, 'no_toy_worker'))

    def test_invalid_submission_does_not_create_shared_record(self):
        with lab.running_fixture() as (base, store, _):
            code, _ = lab.request(base, 'POST', '/repairs', payload={'issue': ' '})
            self.assertEqual(code, 400)
            with store.connection() as db:
                count = db.execute('SELECT COUNT(*) FROM repairs').fetchone()[0]
            self.assertEqual(count, 0)

    def test_store_outage_exposes_misleading_live_check_and_recovers_customer_read(self):
        with lab.running_fixture() as (base, store, router):
            code, created = lab.request(base, 'POST', '/repairs', payload={'issue': 'pump'})
            self.assertEqual(code, 201)
            ident = created['request_id']
            router.healthy[0] = False
            store.available.clear()
            self.assertEqual(lab.request(base, 'GET', '/health/live')[0], 200)
            self.assertEqual(lab.request(base, 'GET', '/health/ready'),
                             (503, {'error': 'store_unavailable'}))
            self.assertEqual(lab.request(base, 'GET', '/repairs/' + ident),
                             (503, {'error': 'store_unavailable'}))
            self.assertEqual(lab.request(base, 'POST', '/repairs', payload={'issue': 'drain'}),
                             (503, {'error': 'store_unavailable'}))
            store.available.set()
            with store.connection() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM repairs').fetchone()[0], 1)
            self.assertEqual(lab.request(base, 'GET', '/health/ready')[0], 200)
            self.assertEqual(lab.request(base, 'GET', '/repairs/' + ident)[1]['issue'], 'pump')

    def test_readiness_reports_worker_and_capacity_limits_separately(self):
        with lab.running_fixture() as (base, store, router):
            with store.hold_slot():
                self.assertEqual(lab.request(base, 'GET', '/health/ready'),
                                 (503, {'error': 'store_busy'}))
            router.healthy[:] = [False, False]
            self.assertEqual(lab.request(base, 'GET', '/health/ready'),
                             (503, {'error': 'no_toy_worker'}))


if __name__ == '__main__':
    unittest.main()
