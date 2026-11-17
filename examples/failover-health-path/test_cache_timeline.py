"""Tests for the timed resolver-cache teaching boundary."""

import unittest

from cache_timeline import Resolver, example, lookup


class CacheTimelineTests(unittest.TestCase):
    def test_existing_caches_keep_original_expiry_after_switch_and_ttl_change(self):
        rows = example()["observations"]
        by_key = {(row["resolver"], row["at"]): row for row in rows}
        self.assertEqual((by_key["A", 110]["answer"], by_key["A", 110]["expires_at"]),
                         ("primary", 300))
        self.assertEqual((by_key["B", 121]["answer"], by_key["B", 121]["expires_at"]),
                         ("primary", 380))
        self.assertEqual((by_key["B", 379]["answer"], by_key["B", 379]["source"]),
                         ("primary", "cache"))

    def test_fresh_and_expired_resolvers_get_new_answer(self):
        rows = example()["observations"]
        by_key = {(row["resolver"], row["at"]): row for row in rows}
        self.assertEqual((by_key["C", 110]["answer"], by_key["C", 110]["source"]),
                         ("standby", "authority"))
        self.assertEqual((by_key["A", 300]["answer"], by_key["A", 300]["expires_at"]),
                         ("standby", 330))
        self.assertEqual((by_key["B", 380]["answer"], by_key["B", 380]["expires_at"]),
                         ("standby", 410))

    def test_lower_ttl_affects_only_an_answer_fetched_after_change(self):
        settings = dict(authority_switch_at=100, ttl_change_at=120,
                        old_ttl=300, new_ttl=30)
        before, after = Resolver(), Resolver()
        self.assertEqual(lookup(before, 119, **settings)["expires_at"], 419)
        self.assertEqual(lookup(before, 121, **settings)["expires_at"], 419)
        self.assertEqual(lookup(after, 121, **settings)["expires_at"], 151)

    def test_rejects_invalid_time_or_ttl(self):
        settings = dict(authority_switch_at=100, ttl_change_at=120,
                        old_ttl=300, new_ttl=30)
        resolver = Resolver()
        lookup(resolver, 20, **settings)
        with self.assertRaises(ValueError):
            lookup(resolver, 19, **settings)
        with self.assertRaises(ValueError):
            lookup(Resolver(), 0, **(settings | {"new_ttl": 0}))
        with self.assertRaises(ValueError):
            lookup(Resolver(), True, **settings)


if __name__ == "__main__":
    unittest.main()
