"""Customer-path checks for the bounded loopback legacy failover model."""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from legacy_failover import LocalLab, run_demo  # noqa: E402


class LegacyFailoverTests(unittest.TestCase):
    def test_customer_loses_node_local_session_and_file_at_switch(self):
        with LocalLab() as lab:
            status, cookie, _ = lab.request("POST", "/login")
            self.assertEqual(status, 200)
            self.assertEqual(lab.request("POST", "/upload", cookie=cookie, data=b"photo-A")[0], 201)
            self.assertEqual(lab.request("GET", "/file", cookie=cookie)[2], b"photo-A")
            lab.stop_primary()
            lab.select_standby()
            self.assertEqual(lab.request("GET", "/health")[0], 200)
            self.assertEqual(lab.request("GET", "/me", cookie=cookie)[0], 401)
            state = json.loads(lab.request("GET", "/inventory", operator=True)[2])
            self.assertFalse(state["file_present"])

    def test_copying_file_repairs_only_one_state_dependency(self):
        with LocalLab() as lab:
            _, cookie, _ = lab.request("POST", "/login")
            lab.request("POST", "/upload", cookie=cookie, data=b"photo-A")
            lab.stop_primary()
            lab.select_standby()
            _, new_cookie, _ = lab.request("POST", "/login")
            self.assertEqual(lab.request("GET", "/file", cookie=new_cookie)[0], 404)
            lab.copy_upload_to_standby()
            self.assertEqual(lab.request("GET", "/me", cookie=cookie)[0], 401)
            self.assertEqual(lab.request("GET", "/file", cookie=new_cookie)[2], b"photo-A")

    def test_operator_inventory_and_unavailable_target_are_distinct(self):
        with LocalLab() as lab:
            self.assertEqual(lab.request("GET", "/inventory")[0], 403)
            lab.stop_primary()
            self.assertEqual(lab.request("GET", "/health")[0], 503)
            lab.select_standby()
            self.assertEqual(lab.request("GET", "/health")[0], 200)

    def test_demo_reports_the_customer_boundary(self):
        result = run_demo()
        self.assertEqual(result["upload_status_on_A"], 201)
        self.assertEqual(result["owner_file_before_failure"], 200)
        self.assertEqual(result["standby_health_after_switch"], 200)
        self.assertEqual(result["old_session_on_B"], 401)
        self.assertFalse(result["file_on_B_before_copy"])
        self.assertTrue(result["file_on_B_after_copy"])
        self.assertEqual(result["old_session_after_file_copy"], 401)
        self.assertEqual(result["new_session_file_after_copy"], 200)


if __name__ == "__main__":
    unittest.main()
