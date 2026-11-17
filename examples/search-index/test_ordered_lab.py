import unittest
from contextlib import closing

from ordered_lab import apply_hint, change_source, new_store, search


class OrderedSearchTests(unittest.TestCase):
    def test_old_hint_cannot_replace_newer_tenant_and_policy(self):
        with closing(new_store()) as db:
            change_source(db, revision=1, tenant='shop-a', body='Returns here')
            change_source(db, revision=2, tenant='shop-b', body='Exchanges here')
            self.assertEqual(apply_hint(db, 2), 'indexed')
            self.assertEqual(apply_hint(db, 1), 'obsolete')
            self.assertEqual(search(db, 'shop-a', 'returns'), [])
            self.assertEqual(search(db, 'shop-b', 'exchanges'), [(1, 'Exchanges here')])

    def test_deletion_is_hidden_before_cleanup_and_old_hint_cannot_revive(self):
        with closing(new_store()) as db:
            change_source(db, revision=1, tenant='shop-a', body='Returns here')
            apply_hint(db, 1)
            change_source(db, revision=2, tenant='shop-a', body='', deleted=True)
            self.assertEqual(search(db, 'shop-a', 'returns'), [])
            self.assertEqual(apply_hint(db, 1), 'obsolete')
            self.assertEqual(apply_hint(db, 2), 'removed')
            self.assertEqual(db.execute('SELECT count(*) FROM entries').fetchone()[0], 0)

    def test_ahead_hint_and_nonincreasing_source_are_rejected(self):
        with closing(new_store()) as db:
            change_source(db, revision=1, tenant='shop-a', body='Returns here')
            with self.assertRaises(ValueError):
                apply_hint(db, 2)
            with self.assertRaises(ValueError):
                change_source(db, revision=1, tenant='shop-b', body='Exchanges here')
            self.assertEqual(apply_hint(db, 1), 'indexed')
            self.assertEqual(search(db, 'shop-a', 'returns'), [(1, 'Returns here')])

    def test_same_hint_replay_does_not_duplicate(self):
        with closing(new_store()) as db:
            change_source(db, revision=1, tenant='shop-a', body='Returns here')
            self.assertEqual(apply_hint(db, 1), 'indexed')
            self.assertEqual(apply_hint(db, 1), 'indexed')
            self.assertEqual(db.execute('SELECT count(*) FROM entries').fetchone()[0], 1)


if __name__ == '__main__':
    unittest.main()
