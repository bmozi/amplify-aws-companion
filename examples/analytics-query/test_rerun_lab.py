"""Publication conditions that prevent a failed or duplicate batch from changing the report."""

import unittest

from rerun_lab import current, open_store, publish, stage


class RerunPublicationTests(unittest.TestCase):
    def setUp(self):
        self.db = open_store()
        stage(self.db, 'v1', 1, [('a', 100), ('b', 200)], ['a', 'b'])
        self.assertEqual(publish(self.db, 'v1', 0), ('published', 1))

    def tearDown(self):
        self.db.close()

    def test_failure_before_stage_commit_cannot_select_a_partial_batch(self):
        original = current(self.db)
        with self.assertRaises(RuntimeError):
            stage(self.db, 'broken-v2', 2, [('a', 100), ('b', 200), ('late', 50)],
                  ['a', 'b', 'late'], fail_after=1)
        self.assertEqual(publish(self.db, 'broken-v2', 1), ('missing_complete_run', 1))
        self.assertEqual(current(self.db), original)
        self.assertEqual(self.db.execute('SELECT count(*) FROM candidate_rows WHERE run_id = ?',
                                         ('broken-v2',)).fetchone()[0], 0)

    def test_rerun_is_idempotent_and_changed_input_under_same_id_is_rejected(self):
        rows = [('a', 100), ('b', 200), ('late', 50)]
        self.assertEqual(stage(self.db, 'v2', 2, rows, ['a', 'b', 'late']), 'staged')
        self.assertEqual(current(self.db)['run_id'], 'v1')
        self.assertEqual(publish(self.db, 'v2', 1), ('published', 2))
        self.assertEqual(stage(self.db, 'v2', 2, list(reversed(rows)), ['late', 'a', 'b']),
                         'already_staged')
        self.assertEqual(publish(self.db, 'v2', 2), ('already_current', 2))
        self.assertEqual((current(self.db)['cents'], len(current(self.db)['rows'])), (350, 3))
        with self.assertRaises(ValueError):
            stage(self.db, 'v2', 2, [('a', 100), ('b', 200), ('late', 55)],
                  ['a', 'b', 'late'])
        self.assertEqual(current(self.db)['cents'], 350)

    def test_stale_generation_and_older_source_cannot_replace_selected_result(self):
        stage(self.db, 'v2', 2, [('a', 100), ('b', 200), ('late', 50)], ['a', 'b', 'late'])
        self.assertEqual(publish(self.db, 'v2', 0), ('stale_generation', 1))
        self.assertEqual(publish(self.db, 'v2', 1), ('published', 2))
        self.assertEqual(publish(self.db, 'v1', 2), ('stale_source_revision', 2))
        self.assertEqual(current(self.db)['run_id'], 'v2')

    def test_missing_expected_event_and_bad_money_cannot_stage(self):
        original = current(self.db)
        with self.assertRaises(ValueError):
            stage(self.db, 'missing', 2, [('a', 100)], ['a', 'b'])
        with self.assertRaises(ValueError):
            stage(self.db, 'overflow', 2, [('a', 2**63)], ['a'])
        with self.assertRaises(ValueError):
            stage(self.db, 'duplicate', 2, [('a', 1), ('a', 1)], ['a'])
        self.assertEqual(current(self.db), original)


if __name__ == '__main__':
    unittest.main()
