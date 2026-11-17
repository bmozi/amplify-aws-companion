"""Consequential state checks at the cancel/send/reconcile boundaries."""

from pathlib import Path
import sqlite3
import tempfile
import unittest

from external_cancel_lab import (approved_operation, reconcile, record_lost_reply,
                                 request_cancel, start_dispatch, state)
from external_effect_lab import (ReplyLost, effect_count, example_action, initialize,
                                 publish)


class ExternalCancellationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.local, self.provider = root / 'workflow.db', root / 'publisher.db'
        self.action = example_action()
        initialize(self.local, self.provider, self.action)
        self.operation = approved_operation(self.local, self.action)

    def test_cancel_before_worker_claim_prevents_this_fixture_send(self):
        self.assertEqual(request_cancel(self.local, self.operation, 'A'),
                         'stopped_before_send')
        self.assertEqual(start_dispatch(self.local, self.operation), 'stopped')
        self.assertEqual(request_cancel(self.local, self.operation, 'A'), 'duplicate')
        self.assertEqual(state(self.local, self.operation), 'cancelled_before_send')
        self.assertEqual(effect_count(self.provider), 0)

    def test_effect_outside_stopped_send_is_a_conflict_not_a_safe_cancel(self):
        self.assertEqual(request_cancel(self.local, self.operation, 'A'),
                         'stopped_before_send')
        # The fixture provider can be called directly; local state is not a security gate.
        publish(self.provider, self.operation, self.action)
        self.assertEqual(reconcile(self.local, self.provider, self.operation),
                         'conflict_after_stop')
        self.assertEqual(state(self.local, self.operation), 'cancelled_before_send')

    def test_cancel_after_claim_then_lost_reply_requires_positive_reconciliation(self):
        self.assertEqual(start_dispatch(self.local, self.operation), 'started')
        self.assertEqual(request_cancel(self.local, self.operation, 'A'),
                         'outcome_unknown')
        with self.assertRaises(ReplyLost):
            publish(self.provider, self.operation, self.action, lose_reply=True)
        self.assertEqual(record_lost_reply(self.local, self.operation), 'cancel_requested')
        self.assertEqual(reconcile(self.local, None, self.operation), 'outcome_unknown')
        self.assertEqual(state(self.local, self.operation), 'cancel_requested')
        self.assertEqual(reconcile(self.local, self.provider, self.operation),
                         'completed_after_cancel')
        self.assertEqual(effect_count(self.provider), 1)
        self.assertEqual(request_cancel(self.local, self.operation, 'A'), 'too_late')

    def test_absent_provider_read_does_not_mean_cancel_succeeded(self):
        self.assertEqual(start_dispatch(self.local, self.operation), 'started')
        self.assertEqual(request_cancel(self.local, self.operation, 'A'),
                         'outcome_unknown')
        self.assertEqual(reconcile(self.local, self.provider, self.operation),
                         'outcome_unknown')
        self.assertEqual(state(self.local, self.operation), 'cancel_requested')
        self.assertEqual(effect_count(self.provider), 0)

    def test_wrong_actor_and_wrong_provider_target_preserve_uncertainty(self):
        self.assertEqual(start_dispatch(self.local, self.operation), 'started')
        with self.assertRaises(PermissionError):
            request_cancel(self.local, self.operation, 'requester')
        self.assertEqual(request_cancel(self.local, self.operation, 'A'),
                         'outcome_unknown')
        with sqlite3.connect(self.provider) as db:
            db.execute('INSERT INTO effects VALUES (?,?,?,?,?)',
                       (self.operation, 'wrong-digest', 'public-site', 'wrong', 'wrong-receipt'))
        self.assertEqual(reconcile(self.local, self.provider, self.operation), 'conflict')
        self.assertEqual(state(self.local, self.operation), 'cancel_requested')

    def test_confirmed_effect_cannot_be_relabelled_as_cancelled(self):
        self.assertEqual(start_dispatch(self.local, self.operation), 'started')
        publish(self.provider, self.operation, self.action)
        self.assertEqual(reconcile(self.local, self.provider, self.operation), 'confirmed')
        self.assertEqual(request_cancel(self.local, self.operation, 'A'), 'too_late')
        self.assertEqual(state(self.local, self.operation), 'confirmed')


if __name__ == '__main__':
    unittest.main()
