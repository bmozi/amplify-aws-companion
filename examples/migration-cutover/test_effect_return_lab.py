"""Data and outside-effect receipts must pass separate local return gates."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from effect_return_lab import (OPERATION, ReplyLost, confirm_target,
                               guarded_return, provider_authorize,
                               replay_confirmed_receipt, setup)
from reverse_lab import replay_target_to_source


class EffectReturnTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.source, self.target, self.pointer, self.provider = setup(Path(temporary.name))
        self.assertEqual(replay_target_to_source(self.source, self.target), 2)

    def test_matching_orders_and_unknown_effect_still_hold_target(self):
        self.assertFalse(guarded_return(self.source, self.target, self.pointer, self.provider))
        self.assertEqual(confirm_target(self.target, None), 'unknown')
        self.assertEqual(self.pointer.read_text(), self.target.name)

    def test_lost_reply_provider_lookup_and_receipt_replay_are_distinct(self):
        with self.assertRaises(ReplyLost):
            provider_authorize(self.provider, lose_reply=True)
        self.assertFalse(guarded_return(self.source, self.target, self.pointer, self.provider))
        self.assertEqual(confirm_target(self.target, self.provider), 'confirmed')
        self.assertFalse(guarded_return(self.source, self.target, self.pointer, self.provider))
        self.assertEqual(replay_confirmed_receipt(self.source, self.target), 1)
        self.assertEqual(replay_confirmed_receipt(self.source, self.target), 0)
        self.assertTrue(guarded_return(self.source, self.target, self.pointer, self.provider))
        self.assertEqual(self.pointer.read_text(), self.source.name)

    def test_conflicting_old_receipt_refuses_replay_and_return(self):
        provider_authorize(self.provider)
        self.assertEqual(confirm_target(self.target, self.provider), 'confirmed')
        with sqlite3.connect(self.source) as db:
            db.execute('INSERT INTO effect_receipts VALUES (?,?,?,?,?)',
                       (OPERATION, 'e', 250, 'wrong-receipt', 'confirmed'))
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            replay_confirmed_receipt(self.source, self.target)
        self.assertFalse(guarded_return(self.source, self.target, self.pointer, self.provider))
        self.assertEqual(self.pointer.read_text(), self.target.name)

    def test_mismatched_provider_evidence_cannot_confirm_effect(self):
        with sqlite3.connect(self.provider) as db:
            db.execute('INSERT INTO authorizations VALUES (?,?,?,?)',
                       (OPERATION, 'e', 999, 'wrong-receipt'))
        self.assertEqual(confirm_target(self.target, self.provider), 'conflict')
        with self.assertRaisesRegex(ValueError, 'no confirmed'):
            replay_confirmed_receipt(self.source, self.target)
        self.assertFalse(guarded_return(self.source, self.target, self.pointer, self.provider))


if __name__ == '__main__':
    unittest.main()
