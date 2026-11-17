"""Failure-boundary checks for the separate-store publication fixture."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from external_effect_lab import (ReplyLost, effect_count, example_action, initialize,
                                 mark_unknown, prepare, publish, reconcile, state)
from two_reviewer_lab import admit, digest, review


class ExternalEffectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.local, self.provider = root / 'local.db', root / 'provider.db'
        self.action = example_action()
        initialize(self.local, self.provider, self.action)

    def approved_operation(self):
        for actor in ('A', 'B'):
            self.assertEqual(review(self.local, self.action['id'], actor,
                                    digest(self.action), 10, 100), 'reviewed')
        self.assertEqual(admit(self.local, self.action['id'], 20), 'admitted')
        return prepare(self.local, self.action)

    def test_lost_reply_is_unknown_until_matching_lookup_and_replay_is_one_effect(self):
        operation = self.approved_operation()
        with self.assertRaises(ReplyLost):
            publish(self.provider, operation, self.action, lose_reply=True)
        mark_unknown(self.local, operation)
        self.assertEqual(state(self.local, operation), 'unknown')
        self.assertEqual(effect_count(self.provider), 1)
        self.assertEqual(reconcile(self.local, None, operation), 'unknown')
        self.assertEqual(reconcile(self.local, self.provider, operation), 'confirmed')
        self.assertEqual(prepare(self.local, self.action), operation)
        self.assertEqual(publish(self.provider, operation, self.action),
                         publish(self.provider, operation, self.action))
        self.assertEqual(effect_count(self.provider), 1)

    def test_admission_and_exact_action_are_required(self):
        with self.assertRaises(ValueError):
            prepare(self.local, self.action)
        self.assertEqual(effect_count(self.provider), 0)
        self.approved_operation()
        altered = {**self.action, 'destination': 'public-site'}
        with self.assertRaises(ValueError):
            prepare(self.local, altered)
        self.assertEqual(effect_count(self.provider), 0)

    def test_same_operation_changed_payload_conflicts(self):
        operation = self.approved_operation()
        publish(self.provider, operation, self.action)
        altered = {**self.action, 'artifact': 'different-fixture'}
        with self.assertRaises(ValueError):
            publish(self.provider, operation, altered)
        self.assertEqual(effect_count(self.provider), 1)

    def test_absent_or_mismatched_provider_record_is_not_completion(self):
        operation = self.approved_operation()
        self.assertEqual(reconcile(self.local, self.provider, operation), 'unknown')
        self.assertEqual(state(self.local, operation), 'pending')
        with sqlite3.connect(self.provider) as db:
            db.execute('INSERT INTO effects VALUES (?,?,?,?,?)',
                       (operation, 'wrong-digest', 'public-site', 'wrong', 'wrong-receipt'))
        self.assertEqual(reconcile(self.local, self.provider, operation), 'conflict')
        self.assertEqual(state(self.local, operation), 'pending')

    def test_matching_digest_with_wrong_target_is_not_completion(self):
        operation = self.approved_operation()
        with sqlite3.connect(self.provider) as db:
            db.execute('INSERT INTO effects VALUES (?,?,?,?,?)',
                       (operation, digest(self.action), 'public-site',
                        self.action['artifact'], 'made-up-receipt'))
        self.assertEqual(reconcile(self.local, self.provider, operation), 'conflict')
        self.assertEqual(state(self.local, operation), 'pending')


if __name__ == '__main__':
    unittest.main()
