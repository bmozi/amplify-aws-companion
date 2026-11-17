import unittest

from lifecycle import trace


class SecretReferenceLifecycleTests(unittest.TestCase):
    def test_rotation_does_not_refresh_template_managed_property(self):
        events = trace("versionless", ["create", "rotate", "refresh_runtime", "update_resource"])
        self.assertTrue(events[0]["injected_works"])
        self.assertFalse(events[1]["injected_works"])
        self.assertFalse(events[1]["runtime_works"])
        self.assertTrue(events[2]["runtime_works"])
        self.assertFalse(events[2]["injected_works"])
        self.assertTrue(events[3]["injected_works"])
        self.assertTrue(all(not event["live_aws_observed"] for event in events))

    def test_pinned_reference_stays_old_after_resource_update(self):
        events = trace("pinned-v1", ["create", "rotate", "update_resource"])
        self.assertEqual(events[-1]["template_injected"], "v1")
        self.assertEqual(events[-1]["store_current"], "v2")
        self.assertFalse(events[-1]["injected_works"])

    def test_failed_refresh_keeps_stale_cache_until_success(self):
        events = trace("versionless", ["create", "rotate", "refresh_failed_keep_cache", "refresh_runtime"])
        self.assertEqual(events[2]["runtime_cache"], "v1")
        self.assertFalse(events[2]["runtime_works"])
        self.assertEqual(events[3]["runtime_cache"], "v2")
        self.assertTrue(events[3]["runtime_works"])
        self.assertFalse(events[3]["injected_works"])

    def test_failed_resource_update_leaves_stale_value_in_this_fixture(self):
        events = trace("versionless", ["create", "rotate", "update_resource_failed", "update_resource"])
        self.assertEqual(events[2]["template_injected"], "v1")
        self.assertFalse(events[2]["injected_works"])
        self.assertEqual(events[3]["template_injected"], "v2")
        self.assertTrue(events[3]["injected_works"])
        self.assertFalse(events[3]["runtime_works"])

    def test_timeline_rejects_unsupported_history(self):
        with self.assertRaises(ValueError):
            trace("versionless", ["rotate"])
        with self.assertRaises(ValueError):
            trace("versionless", ["create", "rotate", "rotate"])
        with self.assertRaises(ValueError):
            trace("versionless", ["create", "create"])


if __name__ == "__main__":
    unittest.main()
