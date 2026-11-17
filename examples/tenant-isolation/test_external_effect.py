"""Changed-condition checks for the synthetic two-store effect exercise."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('external_effect_lab', HERE / 'external_effect_lab.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TwoStoreEffectTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)
        self.lab = MODULE.TwoStoreEffect(path / 'work.sqlite', path / 'provider.sqlite')

    def test_lost_reply_is_unknown_locally_until_receipt_is_joined(self):
        job = self.lab.accept('alice', 'shop-a')
        with self.assertRaises(MODULE.LostReply):
            self.lab.dispatch(job, lose_reply=True)
        restarted = MODULE.TwoStoreEffect(self.lab.work_path, self.lab.provider_path)
        self.assertEqual('pending', restarted.state(job)[2])
        self.assertEqual(1, len(restarted.deliveries()))
        self.assertEqual('confirmed_from_receipt', restarted.reconcile(job))
        self.assertEqual('already_confirmed', restarted.dispatch(job))
        self.assertEqual(1, len(restarted.deliveries()))

    def test_revocation_after_acceptance_does_not_cancel_selected_business_workflow(self):
        job = self.lab.accept('alice', 'shop-a')
        self.lab.revoke('alice', 'shop-a')
        self.assertEqual('confirmed', self.lab.dispatch(job))
        with self.assertRaises(PermissionError):
            self.lab.accept('alice', 'shop-a')

    def test_closure_before_dispatch_stops_pending_work(self):
        job = self.lab.accept('alice', 'shop-a')
        self.lab.close('shop-a')
        self.assertEqual('stopped', self.lab.dispatch(job))
        self.assertEqual([], self.lab.deliveries())

    def test_closure_after_provider_commit_cannot_unsend(self):
        job = self.lab.accept('alice', 'shop-a')
        with self.assertRaises(MODULE.LostReply):
            self.lab.dispatch(job, lose_reply=True)
        self.lab.close('shop-a')
        self.assertEqual('confirmed_from_receipt', self.lab.reconcile(job))
        self.assertEqual(1, len(self.lab.deliveries()))

    def test_closure_between_check_and_provider_commit_is_still_in_flight(self):
        job = self.lab.accept('alice', 'shop-a')
        observed = []

        def close_in_window():
            self.lab.close('shop-a')
            observed.append(self.lab.closure_report('shop-a'))

        with self.assertRaises(MODULE.LostReply):
            self.lab.dispatch(job, lose_reply=True, after_active_check=close_in_window)
        self.assertEqual('closed', observed[0]['access'])
        self.assertEqual('unresolved', observed[0]['effect_review'])
        self.assertEqual(1, len(self.lab.deliveries()))
        self.assertEqual('unresolved', self.lab.closure_report('shop-a')['effect_review'])
        self.assertEqual('confirmed_from_receipt', self.lab.reconcile(job))
        final = self.lab.closure_report('shop-a')
        self.assertEqual('completed_effects_need_retention_review', final['effect_review'])
        self.assertFalse(final['external_copy_deletion_proven'])

    def test_closure_without_accepted_work_does_not_claim_external_deletion(self):
        self.lab.close('shop-a')
        report = self.lab.closure_report('shop-a')
        self.assertEqual('no_unresolved_local_work', report['effect_review'])
        self.assertFalse(report['external_copy_deletion_proven'])

    def test_no_receipt_does_not_become_success(self):
        job = self.lab.accept('alice', 'shop-a')
        self.assertEqual('no_provider_receipt', self.lab.reconcile(job))
        self.assertEqual('pending', self.lab.state(job)[2])
        self.assertEqual([], self.lab.deliveries())

    def test_retry_uses_same_key_and_fixture_provider_effect_once(self):
        job = self.lab.accept('alice', 'shop-a')
        key = self.lab.state(job)[1]
        with self.assertRaises(MODULE.LostReply):
            self.lab.dispatch(job, lose_reply=True)
        self.assertEqual('confirmed', self.lab.dispatch(job))
        self.assertEqual([(key, 'shop-a', f'fictional-receipt-{key}')], self.lab.deliveries())

    def test_tenant_isolation_and_receipt_mismatch(self):
        with self.assertRaises(PermissionError):
            self.lab.accept('alice', 'shop-b')
        a = self.lab.accept('alice', 'shop-a')
        b = self.lab.accept('bob', 'shop-b')
        self.assertEqual('confirmed', self.lab.dispatch(a))
        self.assertEqual('confirmed', self.lab.dispatch(b))
        self.assertEqual({'shop-a', 'shop-b'}, {row[1] for row in self.lab.deliveries()})
        import sqlite3
        key = self.lab.state(a)[1]
        with sqlite3.connect(self.lab.provider_path) as provider:
            provider.execute('UPDATE deliveries SET tenant=? WHERE effect_key=?',
                             ('shop-b', key))
        with sqlite3.connect(self.lab.work_path) as work:
            work.execute("UPDATE outbox SET status='pending',receipt=NULL WHERE id=?", (a,))
        with self.assertRaises(PermissionError):
            self.lab.reconcile(a)


if __name__ == '__main__':
    unittest.main()
